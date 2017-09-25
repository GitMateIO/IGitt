import os
import datetime

import requests_mock

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.Interfaces.Comment import CommentType

from tests import IGittTestCase


class GitLabCommentTest(IGittTestCase):

    def setUp(self):
        token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.comment = GitLabComment(token,
                                     'gitmate-test-user/test', 1,
                                     CommentType.ISSUE, 31500135)
        self.issue_comment = GitLabComment(token,
                                           'gitmate-test-user/test', 30,
                                           CommentType.ISSUE, 32616806)

    def test_number(self):
        self.assertEqual(self.comment.number, 31500135)
        self.assertEqual(self.issue_comment.number, 32616806)

    def test_iid(self):
        self.assertEqual(self.comment.iid, '1')
        self.assertEqual(self.issue_comment.iid, '30')

    def test_type(self):
        self.assertEqual(self.comment.type, CommentType.ISSUE)

    def test_body(self):
        self.assertEqual(self.comment.body, 'Lemme comment on you.\r\n')

    def test_body_setter(self):
        self.issue_comment.body = 'test comment body has changed'
        self.assertEqual(self.issue_comment.body, 'test comment body has changed')
        self.issue_comment.body = 'test comment body to change'
        self.assertEqual(self.issue_comment.body, 'test comment body to change')

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

    def test_repository(self):
        self.assertEqual(self.comment.repository.full_name,
                         'gitmate-test-user/test')
