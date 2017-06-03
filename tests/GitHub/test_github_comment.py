import unittest
import os
import datetime

import vcr
import requests_mock

from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.Interfaces.Comment import CommentType

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class GitHubCommentTest(unittest.TestCase):

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_comment.yaml')
    def setUp(self):
        self.comment = GitHubComment(os.environ.get('GITHUB_TEST_TOKEN', ''),
                                     'gitmate-test-user/test',
                                     CommentType.COMMIT,
                                     22461603)

    def test_type(self):
        self.assertEqual(self.comment.type, CommentType.COMMIT)

    def test_body(self):
        self.assertEqual(self.comment.body, 'test comment on commit')

    def test_author(self):
        self.assertEqual(self.comment.author, 'nkprince007')

    def test_time(self):
        self.assertEqual(self.comment.created,
                         datetime.datetime(2017, 6, 9, 6, 39, 34))
        self.assertEqual(self.comment.updated,
                         datetime.datetime(2017, 6, 9, 6, 39, 34))

    def test_delete(self):
        with requests_mock.Mocker() as m:
            m.delete(requests_mock.ANY, text='{}')
            self.comment.delete()
