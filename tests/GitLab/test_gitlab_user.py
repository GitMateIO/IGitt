import os

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabUser import GitLabUser

from tests import IGittTestCase


class GitLabUserTest(IGittTestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))

        self.user = GitLabUser(self.token, None)
        self.sils = GitLabUser(self.token, 104269)

    def test_user_url(self):
        self.assertEqual(self.sils.url, 'https://gitlab.com/api/v4/users/104269')

    def test_user_id(self):
        self.assertEqual(self.user.identifier, 1369631)
        self.assertEqual(self.sils.identifier, 104269)
