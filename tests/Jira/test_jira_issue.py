import os
import datetime

from IGitt.Jira import JiraOAuth1Token
from IGitt.Jira.JiraIssue import JiraIssue
from IGitt.Interfaces import IssueStates

from tests import IGittTestCase


class JiraIssueTest(IGittTestCase):

    def setUp(self):
        self.token = JiraOAuth1Token(os.environ['JIRA_CLIENT_KEY'],
                                     os.environ['JIRA_TEST_TOKEN'],
                                     os.environ['JIRA_TEST_SECRET'])
        self.iss = JiraIssue(self.token, 10002)

    def test_repo(self):
        with self.assertRaises(NotImplementedError):
            self.assertIsNone(self.iss.repository)

    def test_title(self):
        self.iss.title = 'something else'
        self.assertEqual(self.iss.title, 'something else')

    def test_assignee(self):
        self.assertEqual(self.iss.assignees, {'yuki_is_bored'})
        with self.assertRaises(NotImplementedError):
            self.iss.assignees = {'nkprince007'}

    def test_number(self):
        self.assertEqual(self.iss.number, 10002)
        iss = JiraIssue(self.token, 'LTK-2')
        self.assertEqual(iss.number, 10017)

    def test_description(self):
        self.iss.description = 'new description'
        self.assertEqual(self.iss.description, 'new description')

    def test_author(self):
        self.assertEqual(self.iss.author, 'yuki_is_bored')

    def test_comment(self):
        iss = JiraIssue(self.token, 10001)
        self.assertIn(
            'test comment body has changed',
            {comment.body for comment in iss.comments})
        comment = iss.add_comment('I am a robot.')
        self.assertEqual(comment.body, 'I am a robot.')

    def test_issue_labels(self):
        with self.assertRaises(NotImplementedError):
            self.iss.labels = set()
        with self.assertRaises(NotImplementedError):
            self.assertEqual(self.iss.labels, set())

    def test_time(self):
        self.assertEqual(self.iss.created,
                         datetime.datetime(2018, 3, 16, 13, 16, 28, 562000,
                                           tzinfo=datetime.timezone.utc))
        self.assertEqual(self.iss.updated,
                         datetime.datetime(2018, 3, 21, 15, 3, 53, 963000,
                                           tzinfo=datetime.timezone.utc))

    def test_state(self):
        with self.assertRaises(NotImplementedError):
            self.iss.close()
        self.assertEqual(self.iss.state, IssueStates.OPEN)
        with self.assertRaises(NotImplementedError):
            self.iss.reopen()

    def test_issue_create(self):
        iss = JiraIssue.create(
            self.token, 10001, 'Task', 'test title', 'test body')
        self.assertEqual(iss.state, IssueStates.OPEN)
        self.assertEqual(iss.title, 'test title')

    def test_reactions(self):
        with self.assertRaises(NotImplementedError):
            self.assertEqual(self.iss.reactions, set())

    def test_mrs_closed_by(self):
        with self.assertRaises(NotImplementedError):
            self.assertEqual(self.iss.mrs_closed_by, set())

    def test_hoster(self):
        self.assertEqual(self.iss.hoster, 'jira')

    def test_web_url(self):
        self.assertEqual(self.iss.web_url,
                         'https://jira.gitmate.io:443/browse/KEX-3')
