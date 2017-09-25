import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubNotification import GitHubNotification
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitHub.GitHubThread import GitHubThread

from tests import IGittTestCase


class GitHubNotificationTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.fork_token = GitHubToken(os.environ.get('GITHUB_COAFILE_BOT_TOKEN'))
        temp_repo = GitHubRepository(self.token,
                                     'coafile/issue')
        temp_repo.create_issue('Hello', 'Hello @coafile')

    def test_get_notifications(self):
        notifs = GitHubNotification(self.fork_token)
        threads = notifs.get_threads()
        self.assertIsInstance(threads[0], GitHubThread)
