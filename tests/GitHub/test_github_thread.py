import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubNotification import GitHubNotification
from IGitt.GitHub.GitHubRepository import GitHubRepository

from tests import IGittTestCase


class GitHubThreadTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.repo = GitHubRepository(self.token,
                                     'gitmate-test-user/test')

        self.fork_token = GitHubToken(os.environ.get('GITHUB_COAFILE_BOT_TOKEN', ''))
        self.temp_repo = GitHubRepository(self.token, 'coafile/issue')

    def test_unsubscribe(self):
        self.temp_repo.create_issue('Hello', 'Hello @coafile')
        notifications = GitHubNotification(self.fork_token)
        threads = notifications.get_threads()
        thread = threads[0]
        self.assertIsNone(thread.unsubscribe())

    def test_mark_read(self):
        self.temp_repo.create_issue('Hello', 'Hello @coafile')
        notifications = GitHubNotification(self.fork_token)
        threads = notifications.get_threads()
        thread = threads[0]
        self.assertIsNone(thread.mark())

    def test_reason(self):
        self.temp_repo.create_issue('Hello', 'Hello @coafile')
        notifications = GitHubNotification(self.fork_token)
        threads = notifications.get_threads()
        thread = threads[0]
        self.assertIsInstance(thread.reason, str)

    def test_unread(self):
        self.temp_repo.create_issue('Hello', 'Hello @coafile')
        notifications = GitHubNotification(self.fork_token)
        threads = notifications.get_threads()
        thread = threads[0]
        self.assertIsInstance(thread.unread, bool)
