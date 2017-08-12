"""
This package contains the GitHub implementations of the interfaces in
server.git.Interfaces.
"""
import os
import logging

from IGitt.Interfaces import _fetch, Token
from IGitt.Utils import CachedDataMixin

GH_INSTANCE_URL = os.environ.get('GH_INSTANCE_URL', 'https://github.com')
if not GH_INSTANCE_URL.startswith('http'):  # dont cover cause it'll be removed
    GH_INSTANCE_URL = 'https://' + GH_INSTANCE_URL
    logging.warning('Include the protocol in GH_INSTANCE_URL! Omitting it has '
                    'been deprecated.')
BASE_URL = GH_INSTANCE_URL.replace('github.com', 'api.github.com')


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


def get(token: GitHubToken, url: str, params: dict=None,
        headers: dict=frozenset()):
    """
    Queries GitHub on the given URL for data.

    :param token: An OAuth token.
    :param url: E.g. ``/repo``
    :param params: The query params to be sent.
    :param headers: The request headers to be sent.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(BASE_URL, 'get', token.parameter,
                  url, query_params=params, headers=headers)


def post(token: GitHubToken, url: str, data: dict, headers: dict=frozenset()):
    """
    Posts the given data onto GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param data: The data to post.
    :param headers: The request headers to be sent.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(BASE_URL, 'post', token.parameter, url, data,
                  headers=headers)


def patch(token: GitHubToken, url: str, data: dict, headers: dict=frozenset()):
    """
    Patches the given data onto GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param data: The data to post.
    :param headers: The request headers to be sent.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(BASE_URL, 'patch', token.parameter, url, data,
                  headers=headers)


def delete(token: GitHubToken, url: str, params: dict=None,
           headers: dict=frozenset()):
    """
    Sends a delete request to the given URL on GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param params: The query params to be sent.
    :param headers: The request headers to be sent.
    :raises RuntimeError: If the response indicates any problem.
    """
    _fetch(BASE_URL, 'delete', token.parameter, url, params, headers=headers)


def put(token: GitHubToken, url: str, data: dict, headers: dict=frozenset()):
    """
    Puts the given data onto GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param data: The data to post.
    :param headers: The request headers to be sent.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(BASE_URL, 'put', token.parameter, url, data, headers=headers)
