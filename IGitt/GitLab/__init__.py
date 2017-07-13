"""
This package contains the GitLab implementations of the interfaces in
server.git.Interfaces. GitLab drops the support of API version 3 as of
August 22, 2017. So, IGitt adopts v4 to stay future proof.
"""
import os

from IGitt.Interfaces import Token
from IGitt.Interfaces import _fetch
from IGitt.Utils import CachedDataMixin


GL_INSTANCE_URL = os.environ.get('GL_INSTANCE_URL', 'gitlab.com')
BASE_URL = 'https://' + GL_INSTANCE_URL + '/api/v4'


class GitLabMixin(CachedDataMixin):
    """
    Base object for things that are on GitLab.
    """

    def _get_data(self):
        return get(self._token, self._url)


class GitLabOAuthToken(Token):
    """
    Object representation of OAuth tokens.
    """

    def __init__(self, token):
        self._token = token

    @property
    def parameter(self):
        return {'access_token': self._token}

    @property
    def value(self):
        return self._token


class GitLabPrivateToken(Token):
    """
    Object representation of private tokens.
    """

    def __init__(self, token):
        self._token = token

    @property
    def parameter(self):
        return {'private_token': self._token}

    @property
    def value(self):
        return self._token


def get(token: (GitLabOAuthToken, GitLabPrivateToken), url: str, params: dict=frozenset()):
    """
    Queries GitLab on the given URL for data.

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
                  url, query_params={**dict(params), 'per_page': 100})


def post(token: (GitLabOAuthToken, GitLabPrivateToken), url: str, data: dict):
    """
    Posts the given data onto GitLab.

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


def put(token: (GitLabOAuthToken, GitLabPrivateToken), url: str, data: dict):
    """
    Puts the given data onto GitLab.

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


def delete(token: (GitLabOAuthToken, GitLabPrivateToken), url: str, params: dict=None):
    """
    Sends a delete request to the given URL on GitLab.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param params: The query params to be sent.
    :raises RuntimeError: If the response indicates any problem.
    """
    _fetch(BASE_URL, 'delete', token.parameter,
           url, query_params=params)
