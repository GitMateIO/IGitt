"""
This module contains the helpers for writing testcases for IGitt.
"""
from abc import ABCMeta
from inspect import getfile
import os
from os.path import dirname
from os.path import join
from unittest import TestCase
import re

from vcr import VCR
import pytest


FILTER_QUERY_PARAMS = ['access_token', 'private_token']
FILTER_PARAMS_REGEX = re.compile(r'(\??)((?:{})=\w+&?)'.format(
    '|'.join(FILTER_QUERY_PARAMS)))


# Random private key
PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCZ3CJJ+7vflLg6XPG59kWjfALWJlRtVj1YWmr95dR5a8FRsnwF
Lqgh2vLT2lk2Q6PoXX1C5blsM/xrf0Hc/fw2aOE/RvDCgHG83IBcFv8YOEndgTJp
qBmEK0xIbxhdUtku4xpiZddzyt8KoRg7uHM5P06TX5qJjK5JKL/B4RKnNwIDAQAB
AoGAIxwLqwxJu+RpAdBxzLi4/WxwDUQj4etbBk1jutp2WNrQ+36aNGiIL2mSHevm
ja5zubOTwO9BF8LpJ/KbKf2/TqPlKH4QZibHqoPSAHa6n5RHQBn4f6EauG4IaJfC
nLA5ZyP3T29uCpByM745LUOpteEj/fQCxjYE2y+MsCzdw8ECQQDhMK7psIE7INbN
cUjikA6F0h48ZpDBYPYy+EetwLc45i/fWLd920DxkuQ6zu/qWQWY/x+ZNh/WoYfr
GqVpgszhAkEArukZHcd7z7OCso+2SvWmEmrMprfcOpw/1JsIMt2W9GhnBHe+wBvv
f4jY5iRl/5dKfNXppkz1G1GiXrx7ZOMfFwJADWd1cemUt61Lu+zbVskWZDbOn+/G
/AvGe+A1fA01mshw3w2L1oz/f6GrvihlNYDZCXNeMSN8n6z7xy3N3MrxYQJAHWcw
ArKLHLJXkT7ZbSZ4YXY0qv4TdoLXtBzPtwVLIBEA6F5c4ZyQmUbe92k9AEdljTDE
k2EyfwItInHa6G3JxwJBAIYfzh6YmG/hv0rTgBgKXX0NL+BS/ppcy85w4zg08e/f
Edf3/k7WkC18G802pLT5+xf8snh+Oti95jfoHU1j4ek=
-----END RSA PRIVATE KEY-----
"""

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCZ3CJJ+7vflLg6XPG59kWjfALW
JlRtVj1YWmr95dR5a8FRsnwFLqgh2vLT2lk2Q6PoXX1C5blsM/xrf0Hc/fw2aOE/
RvDCgHG83IBcFv8YOEndgTJpqBmEK0xIbxhdUtku4xpiZddzyt8KoRg7uHM5P06T
X5qJjK5JKL/B4RKnNwIDAQAB
-----END PUBLIC KEY-----
"""

# set environment variables default
ENV_DEFAULTS = {
    'GITLAB_TEST_TOKEN': '',
    'GITHUB_TEST_TOKEN': '',
    'GITHUB_PRIVATE_KEY': PRIVATE_KEY,
    'GITHUB_TEST_APP_ID': '5408',
    'GITHUB_TEST_TOKEN_2': '',
    'GITLAB_TEST_TOKEN_2': '',
}

for key, value in ENV_DEFAULTS.items():
    os.environ.setdefault(key, value)


@pytest.mark.usefixtures('vcrpy_record_mode')
class IGittTestCase(TestCase, metaclass=ABCMeta):
    """
    Base class for writing testcases in IGitt.
    """
    vcr_options = dict()

    @staticmethod
    def remove_link_headers(resp):
        for i, link in enumerate(resp['headers'].get('Link', [])):
            resp['headers']['Link'][i] = FILTER_PARAMS_REGEX.sub(r'\1', link)
        return resp

    @property
    def cassette_name(self):
        """
        Returns the name of the cassette.
        """
        return '{0}.{1}.yaml'.format(self.__class__.__name__,
                                     self._testMethodName)

    @property
    def vcr(self):
        """
        Returns a new vcrpy instance.
        """
        cassettes_dir = join(dirname(getfile(self.__class__)), 'cassettes')
        kwargs = {
            'record_mode': getattr(self, 'vcrpy_record_mode', 'once'),
            'cassette_library_dir': cassettes_dir,
            'match_on': ['method', 'scheme', 'host', 'port', 'path', 'query'],
            'filter_query_parameters': FILTER_QUERY_PARAMS,
            'filter_post_data_parameters': FILTER_QUERY_PARAMS,
            'before_record_response': IGittTestCase.remove_link_headers,
            'filter_headers': ['Link'],
        }
        kwargs.update(self.vcr_options)
        return VCR(**kwargs)

    @classmethod
    def setUpClass(cls):
        """
        On inherited classes, run `setUp` method as usual.

        Inspired via http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class/17696807#17696807
        """
        if cls is not IGittTestCase and cls.setUp is not IGittTestCase.setUp:
            _setup = cls.setUp

            def newSetUp(self, *args, **kwargs):
                IGittTestCase.setUp(self)
                return _setup(self, *args, **kwargs)

            cls.setUp = newSetUp

    def setUp(self):
        """
        Common setup method for all inherited classes.
        """
        my_vcr = self.vcr
        context_manager = my_vcr.use_cassette(self.cassette_name)
        self.cassette = context_manager.__enter__()
        self.addCleanup(context_manager.__exit__, None, None, None)
