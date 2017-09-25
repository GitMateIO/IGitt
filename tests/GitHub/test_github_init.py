from IGitt.GitHub import GitHubToken

from tests import IGittTestCase


class GitHubInitTest(IGittTestCase):

    def test_tokens(self):
        github_token = GitHubToken('test')
        self.assertEqual(github_token.parameter, {'access_token': 'test'})
        self.assertEqual(github_token.value, 'test')
