from os import environ

from IGitt.GitLab import BASE_URL
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab import GitLabPrivateToken
from IGitt.Interfaces import get

from tests import IGittTestCase


class GitLabInitTestCase(IGittTestCase):
    def test_oauth_token(self):
        raw_token = environ.get('GITLAB_TEST_TOKEN', '')
        oauth_token = GitLabOAuthToken(raw_token)
        self.assertEqual(oauth_token.parameter, {})
        self.assertEqual(oauth_token.value, raw_token)
        self.assertEqual(get(oauth_token, BASE_URL + '/user')['username'],
                         'gitmate-test-user')

    def test_private_token(self):
        private_token = GitLabPrivateToken('test')
        self.assertEqual(private_token.parameter, {'private_token': 'test'})
        self.assertEqual(private_token.value, 'test')
