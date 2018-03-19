"""
This package contains the GitLab implementations of the interfaces in
server.git.Interfaces. GitLab drops the support of API version 3 as of
August 22, 2017. So, IGitt adopts v4 to stay future proof.
"""
import os
import logging

from requests_oauthlib import OAuth2

from IGitt.Interfaces import Token, get
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
        return get(self._token, self.url)

    @staticmethod
    def absolute_url(url):
        """
        Makes a URL like ``/repo/coala/coala`` absolute.
        """
        return BASE_URL + url

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
        return self.absolute_url(self._url)

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
    Object representation of OAuth2 tokens.
    """

    def __init__(self, token):
        self._token = token

    @property
    def parameter(self):
        """
        No additional query parameters are used with the token.
        """
        return {}

    @property
    def value(self):
        return self._token

    @property
    def headers(self):
        """
        GitLab OAuth token does not require any special headers.
        """
        return {}

    @property
    def auth(self):
        return OAuth2(token={'access_token': self._token,
                             'token_type': 'bearer'})


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

    @property
    def auth(self):
        """
        Private token based authorization for GitLab cannot be used directly
        via an AuthBase object.
        """
        return None
