import unittest
import os
import datetime

import vcr
import requests_mock

from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.Interfaces.Comment import CommentType

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class GitLabCommentTest(unittest.TestCase):

    def setUp(self):
        self.comment = GitLabComment(os.environ.get('GITLAB_TEST_TOKEN', ''),
                                     'gitmate-test-user/test', 1,
                                     CommentType.ISSUE, 31500135)
        self.issue_comment = GitLabComment(os.environ.get('GITLAB_TEST_TOKEN', ''),
                                           'gitmate-test-user/test', 30,
                                           CommentType.ISSUE, 32616806)

    def test_type(self):
        self.assertEqual(self.comment.type, CommentType.ISSUE)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_comment_body.yaml')
    def test_body(self):
        self.assertEqual(self.comment.body, 'Lemme comment on you.\r\n')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_comment_body_setter.yaml')
    def test_body_setter(self):
        self.issue_comment.body = 'test comment body has changed'
        self.assertEqual(self.issue_comment.body, 'test comment body has changed')
        self.issue_comment.body = 'test comment body to change'
        self.assertEqual(self.issue_comment.body, 'test comment body to change')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_comment_author.yaml')
    def test_author(self):
        self.assertEqual(self.comment.author, 'gitmate-test-user')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_comment_time.yaml')
    def test_time(self):
        self.assertEqual(self.comment.created,
                         datetime.datetime(2017, 6, 5, 5, 20, 28, 418000))
        self.assertEqual(self.comment.updated,
                         datetime.datetime(2017, 6, 5, 6, 5, 34, 491000))

    def test_delete(self):
        with requests_mock.Mocker() as m:
            m.delete(requests_mock.ANY, text='{}')
            self.comment.delete()
