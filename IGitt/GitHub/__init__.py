"""
This package contains the GitHub implementations of the interfaces in
server.git.Interfaces.
"""
import os

from IGitt.Interfaces import _fetch, Token
from IGitt.Utils import CachedDataMixin


GH_INSTANCE_URL = os.environ.get('GH_INSTANCE_URL', 'github.com')
BASE_URL = 'https://api.' + GH_INSTANCE_URL


class GitHubMixin(CachedDataMixin):
    """
    Base object for things that are on GitHub.
    """

    def _get_data(self):
        return get(self._token, self._url)


class GitHubToken(Token):
    """
    Object representation of oauth tokens.
    """

    def __init__(self, token):
        self._token = token

    @property
    def parameter(self):
        return {'access_token': self._token}

    @property
    def value(self):
        return self._token


def get(token: GitHubToken, url: str, params: dict=None):
    """
    Queries GitHub on the given URL for data.

    :param token: An OAuth token.
    :param url: E.g. ``/repo``
    :param params: The query params to be sent.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(BASE_URL, 'get', token.parameter,
                  url, query_params=params)


def post(token: GitHubToken, url: str, data: dict):
    """
    Posts the given data onto GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param data: The data to post.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(BASE_URL, 'post', token.parameter, url, data)


def patch(token: GitHubToken, url: str, data: dict):
    """
    Patches the given data onto GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param data: The data to post.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(BASE_URL, 'patch', token.parameter, url, data)


def delete(token: GitHubToken, url: str, params: dict=None):
    """
    Sends a delete request to the given URL on GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param params: The query params to be sent.
    :raises RuntimeError: If the response indicates any problem.
    """
    _fetch(BASE_URL, 'delete', token.parameter,
           url, params)


def put(token: GitHubToken, url: str, data: dict):
    """
    Puts the given data onto GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param data: The data to post.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(BASE_URL, 'put', token.parameter, url, data)
