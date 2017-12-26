"""
This package contains the GitHub implementations of the interfaces in
server.git.Interfaces.
"""
from datetime import datetime
from datetime import timedelta
from typing import Optional
from typing import Callable
import os
import logging
import time
import requests

from IGitt.Interfaces import _fetch, Token
from IGitt.Utils import CachedDataMixin
import jwt


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
        return BASE_URL + self._url

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
        return {'access_token': self._token}

    @property
    def value(self):
        return self._token


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
                    '/installations/{}/access_tokens'.format(self._id),
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


def get(token: Token,
        url: str,
        params: Optional[dict]=None,
        headers: Optional[dict]=None):
    """
    Queries GitHub on the given URL for data.

    :param token: A Token object.
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

async def lazy_get(url: str,
                   callback: Callable,
                   headers: Optional[dict]=None,
                   timeout: Optional[timedelta]=timedelta(seconds=120),
                   interval: Optional[timedelta]=timedelta(seconds=10)):
    """
    Queries GitHub on the given URL for data, waiting while it
    returns HTTP 202.

    :param url: E.g. ``/repo``
    :param callback:
        The function to callback with data after data is obtained.
        An empty dictionary is sent if nothing is returned by the API.
    :param timeout: datetime.timedelta object with time to keep re-trying.
    :param interval:
        datetime.timedelta object with time to keep in between tries.
    :param headers: The request headers to be sent.
    """
    url = BASE_URL + url
    response = requests.get(url, headers=headers, timeout=3000)

    # Wait and re-request to allow github to process query
    while response.status_code == 202 and timeout.total_seconds() > 0:
        time.sleep(interval.total_seconds())
        timeout -= interval
        response = requests.get(url, headers=headers, timeout=3000)

    await callback(response.json())

def post(token: Token, url: str, data: dict, headers: Optional[dict]=None):
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
    return _fetch(BASE_URL, 'post', token, url, data, headers=headers)


def patch(token: Token, url: str, data: dict, headers: Optional[dict]=None):
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
    return _fetch(BASE_URL, 'patch', token, url, data, headers=headers)


def delete(token: Token,
           url: str,
           params: Optional[dict]=None,
           headers: Optional[dict]=None):
    """
    Sends a delete request to the given URL on GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param params: The query params to be sent.
    :param headers: The request headers to be sent.
    :raises RuntimeError: If the response indicates any problem.
    """
    _fetch(BASE_URL, 'delete', token, url, params, headers=headers)


def put(token: Token, url: str, data: dict, headers: Optional[dict]=None):
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
    return _fetch(BASE_URL, 'put', token, url, data, headers=headers)
