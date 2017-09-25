import unittest
import os

import vcr

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubUser import GitHubUser

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class GitHubUserTest(unittest.TestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))

        self.user = GitHubUser(self.token, 'sils')

    def test_user_url(self):
        self.assertEqual(self.user.url, 'https://github.com/sils')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_user_id.yaml')
    def test_user_id(self):
        self.assertEqual(self.user.identifier, 5716520)
