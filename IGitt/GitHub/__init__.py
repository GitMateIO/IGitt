"""
This package contains the GitHub implementations of the interfaces in
server.git.Interfaces.
"""
from datetime import datetime
from typing import Optional
import os
import logging

from requests_oauthlib import OAuth2
import jwt
import requests

from IGitt.Interfaces import Token, get, post
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
        Returns `github`.
        """
        return 'github'

    @property
    def url(self):
        """
        Returns github API url.
        """
        return self.absolute_url(self._url)

    @property
    def web_url(self):
        """
        Returns the web link for GitHub.
        """
        return self.data['html_url']

    def __repr__(self): # dont cover
        return '<{} object(url={}) at {}>'.format(self.__class__.__name__,
                                                  self.url,
                                                  hex(id(self)))


class GitHubToken(Token):
    """
    Object representation of oauth tokens.
    """

    def __init__(self, token):
        self._token = token

    @property
    def headers(self):
        """
        GitHub Access token does not require any special headers.
        """
        return {}

    @property
    def parameter(self):
        """
        No additional query parameters are used with GitHub token.
        """
        return {}

    @property
    def value(self):
        return self._token

    @property
    def auth(self):
        return OAuth2(token={'access_token': self._token,
                             'token_type': 'bearer'})


class GitHubJsonWebToken(Token):
    """
    Object representation of JSON Web Token.
    """
    def __init__(self, private_key: str, app_id: int):
        self._key = private_key.strip()
        self._app_id = app_id
        self._payload = None
        self._jwt_token = None

    @property
    def payload(self):
        """
        Returns the payload to be sent for JWT encoding.
        """
        if not self._payload:
            self._payload = {
                # issued at time
                'iat': int(datetime.now().timestamp()),
                # JWT expiration time (10 minute maximum), minus 5 seconds just
                # to be sure and cover up the request time
                'exp': int(datetime.now().timestamp() + (10 * 60) - 5),
                # GitHub App's identifier
                'iss': self._app_id
            }
        return self._payload

    # testing over recorded requests is unadvisable as it is dependent on the
    # time of execution of tests
    @property
    def is_expired(self):  # dont cover
        """
        Returns True if the JWT has expired.
        """
        return self.payload['exp'] < datetime.now().timestamp()

    @property
    def headers(self):
        return {'Authorization': 'Bearer {}'.format(self.value),
                'Accept': 'application/vnd.github.machine-man-preview+json'}

    @property
    def parameter(self):
        """
        GitHub's JSON Web Token can only be authenticated via the
        ``Authorization`` header and so, all the nested requests have to be made
        in only that way.
        """
        return {}

    @property
    def value(self):
        if not self._jwt_token or self.is_expired:
            self._jwt_token = jwt.encode(self.payload, self._key, 'RS256')
        return self._jwt_token.decode('utf-8')

    @property
    def auth(self):
        """
        OAuth 2.0 JWT Bearer Token Flow is not supported by oauthlib yet.

        Reference: https://github.com/oauthlib/oauthlib/issues/50
        """
        return None


class GitHubInstallationToken(Token):
    """
    Object representation of GitHub Installation Token.
    """
    def __init__(self,
                 installation_id: int,
                 jwt_token: GitHubJsonWebToken,
                 token: Optional[str]=None,
                 expiry: Optional[datetime]=None):
        self._jwt = jwt_token
        self._expiry = expiry
        self._token = token
        self._id = installation_id

    @property
    def jwt(self):
        """
        Retrieves the JWT being used.
        """
        return self._jwt

    @property
    def headers(self):
        return {'Authorization': 'token {}'.format(self.value),
                'Accept': 'application/vnd.github.machine-man-preview+json'}

    # testing over recorded requests is unadvisable as it is dependent on the
    # time of execution of tests
    @property
    def is_expired(self):  # dont cover
        """
        Returns true if the token has expired.
        """
        if not self._expiry:
            return True
        return datetime.utcnow() > self._expiry

    def _get_new_token(self):
        data = post(self._jwt,
                    BASE_URL+'/installations/{}/access_tokens'.format(self._id),
                    {})
        return data['token'], datetime.strptime(data['expires_at'],
                                                '%Y-%m-%dT%H:%M:%SZ')

    @property
    def value(self):
        if self.is_expired or not self._token:
            self._token, self._expiry = self._get_new_token()
        return self._token

    @property
    def parameter(self):
        """
        GitHub Installation Token can only be authenticated via the
        ``Authorization`` header and so, all the nested requests have to be
        made in only that way.
        """
        return {}

    @property
    def auth(self):
        """
        OAuth 2.0 JWT Bearer Token Flow is not supported by oauthlib yet.

        Reference: https://github.com/oauthlib/oauthlib/issues/50
        """
        return None
