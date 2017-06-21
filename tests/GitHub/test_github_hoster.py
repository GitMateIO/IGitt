import os
import unittest

import vcr

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHub import GitHub

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class TestGitHub(unittest.TestCase):

    def setUp(self):
        self.gh = GitHub(GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', '')))

    @my_vcr.use_cassette('tests/GitHub/cassettes/test_github_hoster_master.yaml')
    def test_master_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gh.master_repositories)),
                         ['GitMateIO/gitmate-2',
                          'GitMateIO/gitmate-2-frontend',
                          'gitmate-test-user/test'])

    @my_vcr.use_cassette('tests/GitHub/cassettes/test_github_hoster_owned.yaml')
    def test_owned_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gh.owned_repositories)),
                         ['gitmate-test-user/test'])

    @my_vcr.use_cassette('tests/GitHub/cassettes/test_github_hoster_write.yaml')
    def test_write_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gh.write_repositories)),
                         ['gitmate-test-user/test', 'sils/gitmate-test'])

    @my_vcr.use_cassette('tests/GitHub/cassettes/test_github_hoster_get_repo.yaml')
    def test_get_repo(self):
        self.assertEqual(self.gh.get_repo('gitmate-test-user/test').full_name,
                         'gitmate-test-user/test')
