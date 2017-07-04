import unittest
import os
import datetime

import vcr
import requests_mock

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.Interfaces.Comment import CommentType

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class GitHubCommentTest(unittest.TestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.comment = GitHubComment(self.token,
                                     'gitmate-test-user/test',
                                     CommentType.COMMIT,
                                     22461603)
        self.issue_comment = GitHubComment(self.token,
                                           'gitmate-test-user/test',
                                           CommentType.ISSUE,
                                           309221241)

    def test_number(self):
        self.assertEqual(self.comment.number, 22461603)
        self.assertEqual(self.issue_comment.number, 309221241)

    def test_type(self):
        self.assertEqual(self.comment.type, CommentType.COMMIT)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_comment_body.yaml')
    def test_body(self):
        self.assertEqual(self.comment.body, 'test comment on commit')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_comment_body_setter.yaml')
    def test_body_setter(self):
        self.issue_comment.body = 'test comment body has changed'
        self.assertEqual(self.issue_comment.body,
                         'test comment body has changed')
        self.issue_comment.body = 'test comment body to change'
        self.assertEqual(self.issue_comment.body,
                         'test comment body to change')


    @my_vcr.use_cassette('tests/GitHub/cassettes/github_comment_author.yaml')
    def test_author(self):
        self.assertEqual(self.comment.author, 'nkprince007')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_comment_time.yaml')
    def test_time(self):
        self.assertEqual(self.comment.created,
                         datetime.datetime(2017, 6, 9, 6, 39, 34))
        self.assertEqual(self.comment.updated,
                         datetime.datetime(2017, 6, 9, 6, 39, 34))

    def test_delete(self):
        with requests_mock.Mocker() as m:
            m.delete(requests_mock.ANY, text='{}')
            self.comment.delete()
