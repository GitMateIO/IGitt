"""
This package contains an abstraction for a git repository.
"""
from enum import Enum
from json.decoder import JSONDecodeError
from typing import Optional

from backoff import on_exception, expo
from requests import Session


HEADERS = {'User-Agent': 'IGitt'}


class IGittObject:
    """
    Any IGitt interface should inherit from this and any IGitt object shall
    have those methods.
    """

    @property
    def hoster(self):
        """
        The hosting service of the object, e.g. 'gitlab' or 'github'.
        """
        raise NotImplementedError


class Token:
    """
    Base class for different types of tokens used for different methods of
    authentications.
    """
    @property
    def headers(self):
        """
        The Authorization headers.
        """
        raise NotImplementedError

    @property
    def value(self):
        """
        Token value
        """
        raise NotImplementedError

    @property
    def parameter(self):
        """
        Parameter to be used for authentication
        """
        raise NotImplementedError


def is_client_error(exception):
    """
    Returns true if the request responded with a client error.
    """
    return 400 <= exception.args[1] < 500


@on_exception(expo, ConnectionError, max_tries=8)
@on_exception(expo, RuntimeError, max_tries=3, giveup=is_client_error)
def get_response(method, *args, **kwargs):
    """
    Sends a request and checks the response for errors, and retries unless it's
    a HTTP client error.
    """
    response = method(*args, **kwargs)
    if response.status_code >= 300:
        raise RuntimeError(response.text, response.status_code)
    return response


def _fetch(base_url: str, req_type: str, token: Token, url: str,
           data: Optional[dict]=None, query_params: Optional[dict]=None,
           headers: Optional[dict]=None):
    """
    Fetch all the contents by following the ``Link`` header.

    :param base_url: The base URL which is used to generate sub URLs.
    :param req_type: A request type. Get, Post, Patch and Delete.
    :param token: A Token object.
    :param url  : E.g. ``/repo``
    :param query_params: The query parameters.
    :param data : The data to post. Used for Patch and Post methods only
    :return     : A dictionary or a list of dictionaries if the response
                  contains multiple items (usually in case of pagination) or a
                  string in case of other format received (e.g. when fetching a
                  git patch or diff) and the HTTP status code.
    """
    data_container = []
    session = Session()
    session.headers.update({**dict(headers or {}), **HEADERS, **token.headers})
    session.params.update({**dict(query_params or {}), **token.parameter})
    req_methods = {
        'get': session.get,
        'post': session.post,
        'put': session.put,
        'patch': session.patch,
        'delete': session.delete
    }
    method = req_methods[req_type]
    resp = get_response(method, base_url + url, json=data)

    # DELETE request returns no response
    if not len(resp.text):
        return []

    while True:
        try:
            if isinstance(resp.json(), dict) and 'items' not in resp.json():
                # if response is a single object
                return resp.json()
            else:
                if isinstance(resp.json(), list):
                    # if response is a list of objects
                    data_container.extend(resp.json())
                elif 'items' in resp.json():
                    # if response is a dict with `items` key
                    data_container.extend(resp.json()['items'])
                if not resp.links.get('next', False):
                    return data_container
                resp = get_response(method,
                                    resp.links.get('next')['url'],
                                    json=data)
        except JSONDecodeError:
            # if the request has a text response, for e.g. a git diff.
            return resp.text


class AccessLevel(Enum):
    """
    Different access levels for users.
    """
    NONE = 0  # in case of private repositories
    CAN_VIEW = 10
    CAN_READ = 20
    CAN_WRITE = 30
    ADMIN = 40
    OWNER = 50
