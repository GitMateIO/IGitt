import unittest
import os

import vcr

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabContent import GitLabContent
from IGitt.GitLab.GitLabRepository import GitLabRepository

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class GitLabContentTest(unittest.TestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.repo = GitLabRepository(self.token, 'gitmate-test-user/test')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_content_get.yaml',
                         filter_query_parameters=['access_token'])
    def test_get_content(self):
        file = GitLabContent(self.token,
                             'gitmate-test-user/test', path='README.md')
        self.assertIsNone(file.get_content())

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_content_delete.yaml',
                         filter_query_parameters=['access_token'])
    def test_delete_content(self):
        self.repo.create_file(path='deleteme', message='hello', content='hello', branch='master')
        file = GitLabContent(self.token,
                             'gitmate-test-user/test', path='deleteme')
        self.assertIsNone(file.delete(message='Delete file'))

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_content_update.yaml',
                         filter_query_parameters=['access_token'])
    def test_update_content(self):
        file = GitLabContent(self.token,
                             'gitmate-test-user/test', path='README.md')
        self.assertIsNone(file.update(message='Update README',
                                      content='I am a test repo! Updated content!'))
