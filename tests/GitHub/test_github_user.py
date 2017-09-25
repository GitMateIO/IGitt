import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubUser import GitHubUser

from tests import IGittTestCase


class GitHubUserTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))

        self.user = GitHubUser(self.token, 'sils')

    def test_user_url(self):
        self.assertEqual(self.user.url, 'https://github.com/sils')

    def test_user_id(self):
        self.assertEqual(self.user.identifier, 5716520)
