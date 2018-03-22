"""
This package contains the JIRA implementations of the interfaces in
server.git.Interfaces.
"""
from urllib.parse import urljoin
import logging
import os

from oauthlib.oauth1 import SIGNATURE_RSA
from requests_oauthlib import OAuth1

from IGitt.Interfaces import get
from IGitt.Interfaces import Token
from IGitt.Utils import CachedDataMixin
from tests import PRIVATE_KEY


JIRA_INSTANCE_URL = os.environ.get('JIRA_INSTANCE_URL',
                                   'https://jira.atlassian.com')
BASE_URL = urljoin(JIRA_INSTANCE_URL, '/rest/api/2')
JIRA_RSA_PRIVATE_KEY_PATH = os.environ.get('JIRA_RSA_PRIVATE_KEY_PATH')
JIRA_RSA_PRIVATE_KEY = PRIVATE_KEY
try:
    JIRA_RSA_PRIVATE_KEY = open(JIRA_RSA_PRIVATE_KEY_PATH, 'r').read().strip()
except (FileNotFoundError, TypeError):
    logging.warning('JIRA REST APIs work only with key signing, please '
                    'include the correct path to your registered RSA private '
                    'key.')


class JiraMixin(CachedDataMixin):
    """
    Base object for all things on Jira.
    """

    def _get_data(self):
        return get(self._token, self.url)

    @staticmethod
    def absolute_url(url):
        """
        Builds an absolute URL from the base URL and specified url.
        """
        return BASE_URL + url

    @property
    def hoster(self):
        """
        Returns `jira`.
        """
        return 'jira'

    @property
    def url(self):
        """
        Returns JIRA API url.
        """
        return self.absolute_url(self._url)

    @property
    def web_url(self):
        """
        Returns the web link for the corresponding JIRA object.
        """
        raise NotImplementedError

    def __repr__(self):  # dont cover
        return '<{} object(url={}) at {}>'.format(self.__class__.__name__,
                                                  self.url,
                                                  hex(id(self)))


class JiraOAuth1Token(Token):
    """
    Object representation of JIRA OAuth v1.0 token.
    """
    def __init__(self, client_key, key, secret):
        self.client_key = client_key
        self.key = key
        self.secret = secret

    @property
    def headers(self):
        return {}

    @property
    def parameter(self):
        return {}

    @property
    def value(self):
        return {'client_key': self.client_key,
                'oauth_token': self.key,
                'oauth_token_secret': self.secret}

    @property
    def auth(self):
        return OAuth1(self.client_key,
                      rsa_key=JIRA_RSA_PRIVATE_KEY,
                      resource_owner_key=self.key,
                      resource_owner_secret=self.secret,
                      signature_method=SIGNATURE_RSA,
                      signature_type='auth_header')
