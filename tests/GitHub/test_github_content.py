import unittest
import os

import vcr

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubContent import GitHubContent
from IGitt.GitHub.GitHubRepository import GitHubRepository

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class GitHubContentTest(unittest.TestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.repo = GitHubRepository(self.token, 'gitmate-test-user/test')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_content_get.yaml',
                         filter_query_parameters=['access_token'])
    def test_get_content(self):
        file = GitHubContent(self.token,
                             'gitmate-test-user/test', path='README.md')
        self.assertIsNone(file.get_content())

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_content_delete.yaml',
                         filter_query_parameters=['access_token'])
    def test_delete_content(self):
        self.repo.create_file(path='deleteme', message='hello', content='hello', branch='master')
        file = GitHubContent(self.token,
                             'gitmate-test-user/test', path='deleteme')
        self.assertIsNone(file.delete(message='Delete file'))

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_content_update.yaml',
                         filter_query_parameters=['access_token'])
    def test_update_content(self):
        file = GitHubContent(self.token,
                             'gitmate-test-user/test', path='README.md')
        self.assertIsNone(file.update(message='Update README',
                                      content='I am a test repo! Updated content!'))
