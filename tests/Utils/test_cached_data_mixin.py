import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubRepository import GitHubRepository

from tests import IGittTestCase


class CachedDataMixinTest(IGittTestCase):

    def test_create_repo(self):
        token = GitHubToken(os.environ['GITHUB_TEST_TOKEN'])
        repository = GitHubRepository(token, 'gitmate-test-user/test')
        repository.refresh()
        # testing some random property for existence
        self.assertEqual(
            repository.clone_url,
            'https://{}@github.com/gitmate-test-user/test.git'.format(
                token.value))
