import unittest
import os
import datetime

import vcr
import requests_mock

from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.Interfaces.Comment import CommentType

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['private_token'],
                 filter_post_data_parameters=['private_token'])


class GitLabCommentTest(unittest.TestCase):

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_comment.yaml')
    def setUp(self):
        self.comment = GitLabComment(os.environ.get('GITLAB_TEST_TOKEN', ''),
                                     'gitmate-test-user/test', 1,
                                     CommentType.ISSUE, 31500135)

    def test_type(self):
        self.assertEqual(self.comment.type, CommentType.ISSUE)

    def test_body(self):
        self.assertEqual(self.comment.body, 'Lemme comment on you.\r\n')

    def test_author(self):
        self.assertEqual(self.comment.author, 'gitmate-test-user')

    def test_time(self):
        self.assertEqual(self.comment.created,
                         datetime.datetime(2017, 6, 5, 5, 20, 28, 418000))
        self.assertEqual(self.comment.updated,
                         datetime.datetime(2017, 6, 5, 6, 5, 34, 491000))

    def test_delete(self):
        with requests_mock.Mocker() as m:
            m.delete(requests_mock.ANY, text='{}')
            self.comment.delete()
