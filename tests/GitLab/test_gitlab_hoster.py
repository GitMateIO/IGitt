import os
import unittest

import vcr

from IGitt.GitLab.GitLab import GitLab

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['private_token'],
                 filter_post_data_parameters=['private_token'])


class TestGitLab(unittest.TestCase):

    @my_vcr.use_cassette('tests/GitLab/cassettes/test_gitlab_hoster.yaml')
    def setUp(self):
        self.gl = GitLab(os.environ.get('GITLAB_TEST_TOKEN', ''))

    @my_vcr.use_cassette('tests/GitLab/cassettes/test_gitlab_hoster_owned.yaml')
    def test_owned_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gl.owned_repositories)),
                         ['gitmate-test-user/test'])

    @my_vcr.use_cassette('tests/GitLab/cassettes/test_gitlab_hoster_write.yaml')
    def test_write_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gl.write_repositories)),
                         ['gitmate-test-user/test', 'nkprince007/gitmate-test'])

    @my_vcr.use_cassette('tests/GitLab/cassettes/test_gitlab_hoster_get_repo.yaml')
    def test_get_repo(self):
        self.assertEqual(self.gl.get_repo('gitmate-test-user/test').full_name,
                         'gitmate-test-user/test')
