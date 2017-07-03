import os
import unittest

from IGitt.Interfaces import error_checked_request, _fetch
from IGitt.GitHub import BASE_URL as GITHUB_BASE_URL
from IGitt.GitLab import BASE_URL as GITLAB_BASE_URL

import vcr

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class TestGitHubInit(unittest.TestCase):

    def test_raises_runtime_error(self):

        @error_checked_request
        def return_300():
            return '', 300

        try:
            return_300()
        except RuntimeError as e:
            self.assertEqual(e.args, ('', 300))

    @staticmethod
    def test_query_params():

        @my_vcr.use_cassette('tests/Interfaces/cassettes/test_query_params.yaml')
        def test_get_query_gitlab():
            _fetch(GITLAB_BASE_URL, 'get',
                   {'access_token': os.environ.get('GITLAB_TEST_TOKEN', '')},
                   '/projects', query_params={'owned': True})

        test_get_query_gitlab()

    @staticmethod
    def test_pagination():

        @my_vcr.use_cassette('tests/Interfaces/cassettes/test_pagination.yaml')
        def cover_fetch_all_github():
            # this is to cover the branch where it handles the pagination
            _fetch(GITHUB_BASE_URL, 'get',
                   {'access_token': os.environ.get('GITHUB_TEST_TOKEN', '')},
                   '/repos/coala/corobo/issues')

        cover_fetch_all_github()

    @staticmethod
    def test_github_search_pagination():

        @my_vcr.use_cassette('tests/Interfaces/cassettes/test_github_search_pagination.yaml')
        def cover_fetch_search_github():
            # this is to cover the pagination format from github search API
            _fetch(GITHUB_BASE_URL, 'get',
                   {'access_token': os.environ.get('GITHUB_TEST_TOKEN', '')},
                   '/search/issues',
                   query_params={'q': ' repo:coala/corobo'})

        cover_fetch_search_github()
