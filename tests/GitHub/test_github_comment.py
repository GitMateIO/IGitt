import os
import datetime

import requests_mock

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.Interfaces.Comment import CommentType

from tests import IGittTestCase


class GitHubCommentTest(IGittTestCase):

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

    def test_body(self):
        self.assertEqual(self.comment.body, 'test comment on commit')

    def test_body_setter(self):
        self.issue_comment.body = 'test comment body has changed'
        self.assertEqual(self.issue_comment.body,
                         'test comment body has changed')
        self.issue_comment.body = 'test comment body to change'
        self.assertEqual(self.issue_comment.body,
                         'test comment body to change')


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

    def test_repository(self):
        self.assertEqual(self.comment.repository.full_name,
                         'gitmate-test-user/test')
