"""
This module contains the helpers for writing testcases for IGitt.
"""
from abc import ABCMeta
from inspect import getfile
from os.path import dirname
from os.path import join
from unittest import TestCase

from vcr import VCR


class IGittTestCase(TestCase, metaclass=ABCMeta):
    """
    Base class for writing testcases in IGitt.
    """
    vcr_options = dict()

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
            'filter_query_parameters': ['access_token', 'private_token'],
            'filter_post_data_parameters': ['access_token', 'private_token']
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

