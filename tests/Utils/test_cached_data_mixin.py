import os
import unittest

import vcr

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubRepository import GitHubRepository


my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'],
                 filter_headers=['Link'])


class CachedDataMixinTest(unittest.TestCase):
    @my_vcr.use_cassette('tests/Utils/cassettes/create_repo.yaml')
    def setUp(self):
        self.token = GitHubToken(os.environ['GITHUB_TEST_TOKEN'])
        self.repository = GitHubRepository(self.token, 'gitmate-test-user/test')
        self.repository.refresh()

    def test_from_data(self):
        repo = GitHubRepository.from_data(
            self.token, 'gitmate-test-user/test', data=self.repository.data)
        self.assertEqual(self.repository.clone_url, repo.clone_url)
