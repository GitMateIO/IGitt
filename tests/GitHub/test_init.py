import os
import unittest

from IGitt.GitHub import error_checked_request, _fetch_all_github

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
    def test_pagination():

        @my_vcr.use_cassette('tests/GitHub/cassettes/github_init.yaml')
        def cover_fetch_all_github():
            # this is to cover the branch where it handles the pagination
            _fetch_all_github('get', os.environ.get('GITHUB_TEST_TOKEN', ''),
                              '/repos/coala/corobo/issues')

        cover_fetch_all_github()
