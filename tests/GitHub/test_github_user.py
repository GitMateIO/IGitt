import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub import GitHubJsonWebToken
from IGitt.GitHub.GitHubUser import GitHubUser

from tests import IGittTestCase


class GitHubUserTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.sils = GitHubUser(self.token, 'sils')
        self.user = GitHubUser(self.token)

    def test_user_url(self):
        self.assertEqual(self.sils.url, 'https://api.github.com/users/sils')
        self.assertEqual(self.sils.web_url, 'https://github.com/sils')

    def test_user_id(self):
        self.assertEqual(self.sils.identifier, 5716520)
        self.assertEqual(self.user.identifier, 16681030)

    def test_username(self):
        self.assertEqual(self.sils.username, 'sils')
        self.assertEqual(self.user.username, 'gitmate-test-user')

    def test_installed_repositories(self):
        self.assertEqual({repo.full_name
                          for repo in self.user.installed_repositories(60731)},
                         {'gitmate-test-org/test'})

    def test_get_installations(self):
        app_token = GitHubToken(os.environ.get('GITHUB_APP_TEST_TOKEN', ''))
        app_user = GitHubUser(app_token)
        jwt = GitHubJsonWebToken(os.environ['GITHUB_PRIVATE_KEY'],
                                 int(os.environ['GITHUB_TEST_APP_ID']))

        self.assertEqual({
            i.app_id for i in app_user.get_installations(jwt)}, {5408})
