import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubRepository import GitHubRepository

from tests import IGittTestCase


class CachedDataMixinTest(IGittTestCase):
    vcr_options = {'filter_headers': ['Link']}

    def test_create_repo(self):
        token = GitHubToken(os.environ['GITHUB_TEST_TOKEN'])
        repository = GitHubRepository(token, 'gitmate-test-user/test')
        repository.refresh()
