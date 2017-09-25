import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubContent import GitHubContent
from IGitt.GitHub.GitHubRepository import GitHubRepository

from tests import IGittTestCase


class GitHubContentTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.repo = GitHubRepository(self.token, 'gitmate-test-user/test')

    def test_get_content(self):
        file = GitHubContent(self.token,
                             'gitmate-test-user/test', path='README.md')
        self.assertIsNone(file.get_content())

    def test_delete_content(self):
        self.repo.create_file(path='deleteme', message='hello', content='hello', branch='master')
        file = GitHubContent(self.token,
                             'gitmate-test-user/test', path='deleteme')
        self.assertIsNone(file.delete(message='Delete file'))

    def test_update_content(self):
        file = GitHubContent(self.token,
                             'gitmate-test-user/test', path='README.md')
        self.assertIsNone(file.update(message='Update README',
                                      content='I am a test repo! Updated content!'))
