import unittest
import os

import vcr

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubNotification import GitHubNotification
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitHub.GitHubThread import GitHubThread


my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class TestGitHubNotification(unittest.TestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.fork_token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN_2'))
        temp_repo = GitHubRepository(self.token,
                                     'gitmate-test-user-2/issue')
        temp_repo.create_issue('Hello', 'Hello @gitmate-test-user-2')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_notifications_get_notifications.yaml')
    def test_get_notifications(self):
        notifs = GitHubNotification(self.fork_token)
        threads = notifs.get_threads()
        self.assertIsInstance(threads[0], GitHubThread)
