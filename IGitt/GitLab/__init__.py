"""
This package contains the GitLab implementations of the interfaces in
server.git.Interfaces. GitLab drops the support of API version 3 as of
August 22, 2017. So, IGitt adopts v4 to stay future proof.
"""
from typing import Optional
from typing import Union
import os
import logging

from IGitt.Interfaces import Token
from IGitt.Interfaces import _fetch
from IGitt.Utils import CachedDataMixin


GL_INSTANCE_URL = os.environ.get('GL_INSTANCE_URL', 'https://gitlab.com')
if not GL_INSTANCE_URL.startswith('http'):  # dont cover cause it'll be removed
    GL_INSTANCE_URL = 'https://' + GL_INSTANCE_URL
    logging.warning('Include the protocol in GL_INSTANCE_URL! Omitting it has '
                    'been deprecated.')

BASE_URL = GL_INSTANCE_URL + '/api/v4'


class GitLabMixin(CachedDataMixin):
    """
    Base object for things that are on GitLab.
    """

    def _get_data(self):
        return get(self._token, self._url)

    @property
    def hoster(self):
        """
        Tells you that this is a `gitlab` object.
        """
        return 'gitlab'

    @property
    def url(self):
        """
        Returns gitlab API url.
        """
        return BASE_URL + self._url

    @property
    def web_url(self):
        """
        Returns a web link for GitLab.
        """
        return self.data['web_url']

    def __repr__(self): # dont cover
        return '<{} object(url={}) at {}>'.format(self.__class__.__name__,
                                                  self.url,
                                                  hex(id(self)))


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

    @property
    def headers(self):
        """
        GitLab OAuth token does not require any special headers.
        """
        return {}


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

    @property
    def headers(self):
        """
        GitLab Private token does not require any special headers.
        """
        return {}


def get(token: Union[GitLabOAuthToken, GitLabPrivateToken], url: str,
        params: Optional[dict]=None, headers: Optional[dict]=None):
    """
    Queries GitLab on the given URL for data.

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
    return _fetch(BASE_URL, 'get', token,
                  url, query_params={**dict(params or {}), 'per_page': 100},
                  headers=headers)


def post(token: Union[GitLabOAuthToken, GitLabPrivateToken],
         url: str,
         data: dict,
         headers: Optional[dict]=None):
    """
    Posts the given data onto GitLab.

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
    return _fetch(BASE_URL, 'post', token, url, data, headers=headers)


def put(token: Union[GitLabOAuthToken, GitLabPrivateToken],
        url: str,
        data: dict,
        headers: Optional[dict]=None):
    """
    Puts the given data onto GitLab.

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
    return _fetch(BASE_URL, 'put', token, url, data, headers=headers)


def delete(token: Union[GitLabOAuthToken, GitLabPrivateToken], url: str,
           params: Optional[dict]=None, headers: Optional[dict]=None):
    """
    Sends a delete request to the given URL on GitLab.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param params: The query params to be sent.
    :param headers: The request headers to be sent.
    :raises RuntimeError: If the response indicates any problem.
    """
    _fetch(BASE_URL, 'delete', token,
           url, query_params=params, headers=headers)
