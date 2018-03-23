import os
import datetime

import requests_mock

from IGitt.Jira import JiraOAuth1Token
from IGitt.Jira.JiraComment import JiraComment
from IGitt.Interfaces.Comment import CommentType

from tests import IGittTestCase


class JiraCommentTest(IGittTestCase):

    def setUp(self):
        self.token = JiraOAuth1Token(os.environ['JIRA_CLIENT_KEY'],
                                     os.environ['JIRA_TEST_TOKEN'],
                                     os.environ['JIRA_TEST_SECRET'])
        self.comment = JiraComment(self.token, 10001, 10001)

    def test_number(self):
        self.assertEqual(self.comment.number, 10001)

    def test_type(self):
        self.assertEqual(self.comment.type, CommentType.ISSUE)

    def test_body(self):
        self.assertEqual(self.comment.body,
                         'Created 1 days ago\r\nBacklog to Selected for '
                         'Development 5 hours 12 minutes ago')

    def test_body_setter(self):
        self.comment.body = 'test comment body has changed'
        self.assertEqual(self.comment.body, 'test comment body has changed')

    def test_author(self):
        with self.assertRaises(NotImplementedError):
            self.assertEqual(self.comment.author, 'yuki_is_bored')

    def test_time(self):
        self.assertEqual(self.comment.created,
                         datetime.datetime(2018, 3, 16, 8, 4, 27, 968000,
                                           tzinfo=datetime.timezone.utc))
        self.assertEqual(self.comment.updated,
                         datetime.datetime(2018, 3, 23, 13, 26, 10, 33000,
                                           tzinfo=datetime.timezone.utc))

    def test_delete(self):
        with requests_mock.Mocker() as m:
            m.delete(requests_mock.ANY, text='{}')
            self.comment.delete()

    def test_repository(self):
        with self.assertRaises(NotImplementedError):
            self.assertEqual(self.comment.repository.full_name,
                             'gitmate-test-user/test')
