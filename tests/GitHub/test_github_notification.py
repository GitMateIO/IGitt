import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubNotification import GitHubNotification
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitHub.GitHubThread import GitHubThread

from tests import IGittTestCase


class GitHubNotificationTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.fork_token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN_2'))
        temp_repo = GitHubRepository(self.token,
                                     'gitmate-test-user-2/issue')
        temp_repo.create_issue('Hello', 'Hello @gitmate-test-user-2')

    def test_get_notifications(self):
        notifs = GitHubNotification(self.fork_token)
        threads = notifs.get_threads()
        self.assertIsInstance(threads[0], GitHubThread)
