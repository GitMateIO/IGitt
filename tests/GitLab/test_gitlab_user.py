import unittest
import os

import vcr

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabUser import GitLabUser

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class GitLabUserTest(unittest.TestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))

        self.user = GitLabUser(self.token, None)
        self.sils = GitLabUser(self.token, 104269)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_user_url.yaml')
    def test_user_url(self):
        self.assertEqual(self.user.url, 'https://gitlab.com/gitmate-test-user')
        self.assertEqual(self.sils.url, 'https://gitlab.com/sils')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_user_id.yaml')
    def test_user_id(self):
        self.assertEqual(self.user.identifier, 1369631)
        self.assertEqual(self.sils.identifier, 104269)
