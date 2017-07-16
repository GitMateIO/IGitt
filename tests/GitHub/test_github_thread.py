import unittest
import os

import vcr

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubNotification import GitHubNotification
from IGitt.GitHub.GitHubRepository import GitHubRepository


my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class TestGitHubThread(unittest.TestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.repo = GitHubRepository(self.token,
                                     'gitmate-test-user/test')

        self.fork_token = GitHubToken(os.environ.get('GITHUB_COAFILE_BOT_TOKEN', ''))
        self.temp_repo = GitHubRepository(self.token, 'coafile/issue')


    @my_vcr.use_cassette('tests/GitHub/cassettes/github_thread_unsubscribe.yaml')
    def test_unsubscribe(self):
        self.temp_repo.create_issue('Hello', 'Hello @coafile')
        notifications = GitHubNotification(self.fork_token)
        threads = notifications.get_threads()
        thread = threads[0]
        self.assertIsNone(thread.unsubscribe())

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_thread_mark_read.yaml')
    def test_mark_read(self):
        self.temp_repo.create_issue('Hello', 'Hello @coafile')
        notifications = GitHubNotification(self.fork_token)
        threads = notifications.get_threads()
        thread = threads[0]
        self.assertIsNone(thread.mark())

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_thread_reason.yaml')
    def test_reason(self):
        self.temp_repo.create_issue('Hello', 'Hello @coafile')
        notifications = GitHubNotification(self.fork_token)
        threads = notifications.get_threads()
        thread = threads[0]
        self.assertIsInstance(thread.reason, str)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_thread_unread.yaml')
    def test_unread(self):
        self.temp_repo.create_issue('Hello', 'Hello @coafile')
        notifications = GitHubNotification(self.fork_token)
        threads = notifications.get_threads()
        thread = threads[0]
        self.assertIsInstance(thread.unread, bool)
