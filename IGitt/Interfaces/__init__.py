"""
This package contains an abstraction for a git repository.
"""
from enum import Enum
from functools import wraps
from json.decoder import JSONDecodeError
from typing import Optional

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


def error_checked_request(func):
    """
    Create an error check wrapper augmenting ``func`` to perform the given
    request and check the response for errors.
    """
    @wraps(func)
    def wrap_func(*args, **kwargs):
        """
        Perform the given request and checks the response for errors.
        Any arguments are passed through to ``func``.

        :raises RuntimeError: If the response indicates any problem.
        """
        response, code = func(*args, **kwargs)
        if code >= 300:
            raise RuntimeError(response, code)

        return response
    return wrap_func


@error_checked_request
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
    fetch_method = req_methods[req_type]
    resp = fetch_method(base_url + url, json=data)

    # Delete request returns no response
    if not len(resp.text):
        return [], resp.status_code

    while resp.links.get('next', False):
        if isinstance(resp.json(), dict):
            data_container.extend(resp.json()['items'])
        else:
            data_container.extend(resp.json())
        resp = fetch_method(resp.links.get('next')['url'], json=data)

    try:
        if isinstance(resp.json(), dict):
            if 'items' in resp.json():
                data_container.extend(resp.json()['items'])
                return data_container, resp.status_code
            else:
                return resp.json(), resp.status_code
    except JSONDecodeError:
        return resp.text, resp.status_code

    # Add the last node data
    data_container.extend(resp.json())
    return data_container, resp.status_code


class AccessLevel(Enum):
    """
    Different access levels for users.
    """
    CAN_VIEW = 10
    CAN_READ = 20
    CAN_WRITE = 30
    ADMIN = 40
    OWNER = 50
