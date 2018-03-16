"""
This package contains the GitHub implementations of the interfaces in
server.git.Interfaces.
"""
from urllib.parse import urljoin
from typing import Dict
from typing import Optional
import logging
import os

from oauthlib.oauth1 import SIGNATURE_RSA
from requests_oauthlib import OAuth1Session

from IGitt.Interfaces import _fetch
from IGitt.Interfaces import Token
from tests import PRIVATE_KEY


JIRA_INSTANCE_URL = os.environ.get('JIRA_INSTANCE_URL',
                                   'https://jira.atlassian.com')
BASE_URL = urljoin(JIRA_INSTANCE_URL, '/rest/api/2')
JIRA_RSA_PRIVATE_KEY_PATH = os.environ.get('JIRA_RSA_PRIVATE_KEY_PATH')
JIRA_RSA_PRIVATE_KEY = PRIVATE_KEY
try:
    JIRA_RSA_PRIVATE_KEY = open(JIRA_RSA_PRIVATE_KEY_PATH, 'r').read().strip()
except (FileNotFoundError, TypeError):
    logging.warning('JIRA REST APIs only work with key signing, please include'
                    ' the correct path to your registered RSA private key.')


class JiraToken(Token):
    """
    Object representation of OAuth Tokens for JIRA.
    """

    def __init__(self, client_key, token, secret):
        self.client_key = client_key
        self.key = token
        self.secret = secret
        self._session = None

    @property
    def headers(self):
        return {}

    @property
    def parameter(self):
        return {}

    @property
    def value(self):
        return 'oauth_token={}&oauth_token_secret={}'.format(
            self.key, self.secret)

    @property
    def session(self):
        """
        Returns a configured OAuth1Session instance that can be readily used to
        authenticate any request.
        """
        if not self._session:
            self._session = OAuth1Session(self.client_key,
                                          resource_owner_key=self.key,
                                          resource_owner_secret=self.secret,
                                          signature_method=SIGNATURE_RSA,
                                          signature_type='auth_header',
                                          rsa_key=JIRA_RSA_PRIVATE_KEY)
        return self._session


def get(token: JiraToken,
        url: str,
        params: Optional[Dict]=None,
        headers: Optional[Dict]=None):
    """
    Queries JIRA on the given URL for data.

    :param token:
        A JiraToken object which represents an OAuth1 token.
    :param url:
        The URL to be queried for. e.g. `/project`
    :param params:
        The query params to be sent, if any.
    :param headers:
        The request headers to be sent, if any.
    :return:
        A dictionary or a list of dictionary if the response contains multiple
        items (usually in case of pagination) and the HTTP status code.
    :raises RunTimeError:
        If the response indicates any problem.
    """
    return _fetch(BASE_URL, 'get', token, url, session=token.session,
                  query_params={**dict(params or {})}, headers=headers)
