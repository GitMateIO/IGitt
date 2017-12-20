import os

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabUser import GitLabUser

from tests import IGittTestCase


class GitLabUserTest(IGittTestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.user = GitLabUser(self.token)
        self.sils = GitLabUser(self.token, 104269)

    def test_user_url(self):
        self.assertEqual(self.sils.url, 'https://gitlab.com/api/v4/users/104269')
        self.assertEqual(self.sils.web_url, 'https://gitlab.com/sils')

    def test_user_id(self):
        self.assertEqual(self.user.identifier, 1369631)
        self.assertEqual(self.sils.identifier, 104269)

    def test_username(self):
        self.assertEqual(self.sils.username, 'sils')
        self.assertEqual(self.user.username, 'gitmate-test-user')

    def test_from_username(self):
        user = GitLabUser.from_username(self.token, 'sils')
        self.assertEqual(user.username, 'sils')
        self.assertEqual(user.identifier, 104269)
