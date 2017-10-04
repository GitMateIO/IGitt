"""
This package contains the GitHub implementations of the interfaces in
server.git.Interfaces.
"""
from datetime import datetime
import os
import logging

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
        raise NotImplementedError

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
        self._key = private_key
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
                'iat': int(datetime.utcnow().timestamp()),
                # JWT expiration time (10 minute maximum)
                'exp': int(datetime.utcnow().timestamp() + (10 * 60)),
                # GitHub App's identifier
                'iss': self._app_id
            }
        return self._payload

    @property
    def is_expired(self):
        """
        Returns True if the JWT has expired.
        """
        return self.payload['exp'] < datetime.utcnow().timestamp()

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
        raise NotImplementedError

    @property
    def value(self):
        if not self._jwt_token or self.is_expired:
            self._jwt_token = jwt.encode(self.payload, self._key, 'RS256')
        return self._jwt_token.decode('utf-8')


def get(token: Token,
        url: str,
        params: dict=None,
        headers: dict=frozenset()):
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
                  url, query_params=params, headers=headers)


def post(token: Token, url: str, data: dict, headers: dict=frozenset()):
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


def patch(token: Token, url: str, data: dict, headers: dict=frozenset()):
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


def delete(token: Token, url: str, params: dict=None,
           headers: dict=frozenset()):
    """
    Sends a delete request to the given URL on GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param params: The query params to be sent.
    :param headers: The request headers to be sent.
    :raises RuntimeError: If the response indicates any problem.
    """
    _fetch(BASE_URL, 'delete', token, url, params, headers=headers)


def put(token: Token, url: str, data: dict, headers: dict=frozenset()):
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
