"""
This package contains an abstraction for a git repository.
"""
from base64 import b64encode
from collections import defaultdict
from datetime import timedelta
from enum import Enum
from json.decoder import JSONDecodeError
import time
from typing import Callable
from typing import Dict
from typing import Optional

from backoff import on_exception, expo
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
import requests


HEADERS = {'User-Agent': 'IGitt'}
_RESPONSES = defaultdict()


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

    @property
    def url(self):
        """
        Returns API url.
        """
        raise NotImplementedError

    @property
    def web_url(self):
        """
        Returns the web link.
        """
        raise NotImplementedError

    def __eq__(self, other):
        """
        Wether or not self is equal to another object :)
        """
        return hash(self) == hash(other)

    def __hash__(self):
        """
        A unique hash.
        """
        return hash(self.url)


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

    @property
    def auth(self):
        """
        A AuthBase instance that can be readily used to configure any kind of
        authentication easily with requests library.
        """
        raise NotImplementedError


class BasicAuthorizationToken(Token):
    """
    Basic HTTP Authorization using username and password.
    """
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self._encoded = None

    @property
    def value(self):
        if not self._encoded:
            self._encoded = b64encode(bytes('{}:{}'.format(
                self.username, self.password), 'utf-8'))
        return self._encoded

    @property
    def headers(self):
        """
        Addtional headers are not required as HTTPBasicAuth is being used.
        """
        return {}

    @property
    def parameter(self):
        """
        Basic HTTP Authentication only refers to use of `Authorization` Header.
        """
        return {}

    @property
    def auth(self):
        return HTTPBasicAuth(self.username, self.password)


def is_client_error_or_unmodified(exception):
    """
    Returns true if the request responded with a client error.
    """
    return (400 <= exception.args[1] < 500) or (exception.args[1] == 304)


@on_exception(expo, ConnectionError, max_tries=8)
@on_exception(expo,
              RuntimeError,
              max_tries=3,
              giveup=is_client_error_or_unmodified)
def get_response(method: Callable,
                 url: str,
                 auth: AuthBase,
                 json: Optional[Dict]=frozenset()):
    """
    Sends a request and checks the response for errors, and retries unless it's
    a HTTP client error.
    """
    headers = ({'If-None-Match': _RESPONSES[url].headers.get('ETag')}
               if url in _RESPONSES else {})
    response = method(url, auth=auth, json=dict(json or {}), headers=headers)
    if response.status_code == 304 and url in _RESPONSES:
        return _RESPONSES[url]
    elif response.status_code >= 300:
        raise RuntimeError(response.text, response.status_code)
    _RESPONSES[url] = response
    return response


def _fetch(url: str, req_type: str, token: Token, data: Optional[dict]=None,
           query_params: Optional[dict]=None, headers: Optional[dict]=None):
    """
    Fetch all the contents by following the ``Link`` header.

    :param url:
        The URL to query.
    :param req_type:
        The request type. Get, Post, Patch and Delete.
    :param token:
        The Token object to be used for authentication.
    :param data:
        The data to post. Used for PATCH and POST methods only.
    :param query_params:
        Any additional query parameters that should be sent with the request.
    :param headers:
        Any additional headers that should be sent with request.
    :return:
        A dictionary or a list of dictionaries if the response contains
        multiple items (usually in case of pagination) or a string in case of
        other format received (e.g. when fetching a git patch or diff) and the
        corresponding HTTP status code.
    """
    data_container = []
    session = requests.Session()
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
    resp = get_response(method, url, token.auth, json=data)

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
                                    token.auth,
                                    json=data)
        except JSONDecodeError:
            # if the request has a text response, for e.g. a git diff.
            return resp.text

def get(token: Token, url: str, params: Optional[dict]=None,
        headers: Optional[dict]=None):
    """
    Queries the given URL for data.

    :param token: A token.
    :param url: The URL to access.
    :param params: The query params to be sent.
    :param headers: The request headers to be sent.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(url, 'get', token,
                  query_params={**dict(params or {}), 'per_page': 100},
                  headers=headers)


def post(token: Token, url: str, data: dict, headers: Optional[dict]=None):
    """
    Posts the given data to the given URL.

    :param token: A token.
    :param url: The URL to access.
    :param data: The data to post.
    :param headers: The request headers to be sent.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(url, 'post', token, data, headers=headers)


def put(token: Token, url: str, data: dict, headers: Optional[dict]=None):
    """
    Puts the given data to the given URL.

    :param token: A token.
    :param url: The URL to access.
    :param data: The data to put.
    :param headers: The request headers to be sent.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(url, 'put', token, data, headers=headers)


def patch(token: Token, url: str, data: dict, headers: Optional[dict]=None):
    """
    Patches the given data to the given URL.

    :param token: A token.
    :param url: The URL to access.
    :param data: The data to patch.
    :param headers: The request headers to be sent.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(url, 'patch', token, data, headers=headers)


def delete(token:Token, url: str, data: Optional[dict]=None,
           headers: Optional[dict]=None, params: Optional[dict]=None):
    """
    Sends a delete request to the given URL.

    :param token: A token.
    :param url: The URL to access.
    :param params: The query params to be sent.
    :param headers: The request headers to be sent.
    :raises RuntimeError: If the response indicates any problem.
    """
    _fetch(url, 'delete', token, data, query_params=params, headers=headers)


async def lazy_get(url: str,
                   callback: Callable,
                   headers: Optional[dict]=None,
                   timeout: Optional[timedelta]=timedelta(seconds=120),
                   interval: Optional[timedelta]=timedelta(seconds=10)):
    """
    Queries GitHub on the given URL for data, waiting while it
    returns HTTP 202.

    :param url: The full URL to query.
    :param callback:
        The function to callback with data after data is obtained.
        An empty dictionary is sent if nothing is returned by the API.
    :param timeout: datetime.timedelta object with time to keep re-trying.
    :param interval:
        datetime.timedelta object with time to keep in between tries.
    :param headers: The request headers to be sent.
    """
    response = requests.get(url, headers=headers, timeout=3000)

    # Wait and re-request to allow github to process query
    while response.status_code == 202 and timeout.total_seconds() > 0:
        time.sleep(interval.total_seconds())
        timeout -= interval
        response = requests.get(url, headers=headers, timeout=3000)

    await callback(response.json())


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

class MergeRequestStates(Enum):
    """
    This class depicts the merge request states that can are present in any
    hosting service providers like GitHub or GitLab.
    """
    OPEN = 'open'
    CLOSED = 'closed'
    MERGED = 'merged'

class IssueStates(Enum):
    """
    This class depicts the issue states that can are present in any hosting
    service providers like GitHub or GitLab.
    """
    def __str__(self):
        """
        Make behaviour of object as similar to a string as possible.
        """
        return str(self.value)

    OPEN = 'open'
    CLOSED = 'closed'
