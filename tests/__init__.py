"""
This module contains the helpers for writing testcases for IGitt.
"""
from abc import ABCMeta
from inspect import getfile
from os.path import dirname
from os.path import join
from unittest import TestCase
import re

from vcr import VCR


FILTER_QUERY_PARAMS = ['access_token', 'private_token']
FILTER_PARAMS_REGEX = re.compile(r'(\??)((?:{})=\w+&?)'.format(
    '|'.join(FILTER_QUERY_PARAMS)))


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
