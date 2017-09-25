import os

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabContent import GitLabContent
from IGitt.GitLab.GitLabRepository import GitLabRepository

from tests import IGittTestCase


class GitLabContentTest(IGittTestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.repo = GitLabRepository(self.token, 'gitmate-test-user/test')

    def test_get_content(self):
        file = GitLabContent(self.token,
                             'gitmate-test-user/test', path='README.md')
        self.assertIsNone(file.get_content())

    def test_delete_content(self):
        self.repo.create_file(path='deleteme', message='hello', content='hello', branch='master')
        file = GitLabContent(self.token,
                             'gitmate-test-user/test', path='deleteme')
        self.assertIsNone(file.delete(message='Delete file'))

    def test_update_content(self):
        file = GitLabContent(self.token,
                             'gitmate-test-user/test', path='README.md')
        self.assertIsNone(file.update(message='Update README',
                                      content='I am a test repo! Updated content!'))
