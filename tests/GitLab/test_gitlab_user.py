import os

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabUser import GitLabUser

from tests import IGittTestCase


class GitLabUserTest(IGittTestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.user = GitLabUser(self.token)
        self.sils = GitLabUser(self.token, 'sils')

    def test_user_url(self):
        self.assertEqual(self.sils.url, 'https://gitlab.com/api/v4/users/104269')
        self.assertEqual(self.sils.web_url, 'https://gitlab.com/sils')

    def test_user_id(self):
        self.assertEqual(self.user.identifier, 1369631)
        self.assertEqual(self.sils.identifier, 104269)

    def test_username(self):
        self.assertEqual(self.sils.username, 'sils')
        self.assertEqual(self.user.username, 'gitmate-test-user')

    def test_assigend_issues(self):
        self.assertEqual(list(map(lambda x: x.number,
                                  self.user.assigned_issues())),
                         [35, 32, 1])
        self.assertEqual(list(map(lambda x: x.number,
                                  self.sils.assigned_issues())),
                         [236, 233, 228, 222, 220, 48, 46, 172, 73, 169, 161,
                          137, 40, 135, 126, 103, 97, 64, 96, 89, 70, 63, 56,
                          44, 60, 35, 45, 14, 13, 12, 11, 10, 9, 7, 6, 3, 22,
                          13, 12, 11, 10, 13, 4, 5, 2])
