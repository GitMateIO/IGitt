from IGitt.GitLab import GitLabOAuthToken, GitLabPrivateToken

from tests import IGittTestCase

class GitLabInitTestCase(IGittTestCase):
    def test_oauth_token(self):
        oauth_token = GitLabOAuthToken('test')
        self.assertEqual(oauth_token.parameter, {'access_token': 'test'})
        self.assertEqual(oauth_token.value, 'test')

    def test_private_token(self):
        private_token = GitLabPrivateToken('test')
        self.assertEqual(private_token.parameter, {'private_token': 'test'})
        self.assertEqual(private_token.value, 'test')
