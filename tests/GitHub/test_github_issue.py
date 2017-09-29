import os
import datetime

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubIssue import GitHubIssue

from tests import IGittTestCase


class GitHubIssueTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.iss = GitHubIssue(self.token,
                               'gitmate-test-user/test', 39)

    def test_repo(self):
        self.assertEqual(self.iss.repository.full_name,
                         'gitmate-test-user/test')

    def test_title(self):
        self.iss.title = 'new title'
        self.assertEqual(self.iss.title, 'new title')

    def test_assignee(self):
        self.assertEqual(self.iss.assignees, set())
        iss = GitHubIssue(self.token,
                          'gitmate-test-user/test', 41)
        iss.assign('meetmangukiya')
        self.assertEqual(iss.assignees, {'meetmangukiya'})
        iss.unassign('meetmangukiya')
        self.assertEqual(iss.assignees, set())
        iss = GitHubIssue(self.token, 'gitmate-test-user/test', 107)
        self.assertEqual(iss.assignees, set())

    def test_number(self):
        self.assertEqual(self.iss.number, 39)

    def test_description(self):
        self.assertEqual(self.iss.description, 'test description\r\n')

    def test_author(self):
        self.assertEqual(self.iss.author, 'meetmangukiya')

    def test_comment(self):
        self.iss.add_comment('this is a comment')
        self.assertEqual(self.iss.comments[0].body, 'this is a comment')

    def test_issue_labels(self):
        self.iss.labels = set()
        self.assertEqual(self.iss.labels, set())
        self.iss.labels = self.iss.labels | {'dem'}
        self.iss.labels = self.iss.labels  # Doesn't do a request :)
        self.assertEqual(len(self.iss.available_labels), 4)

    def test_time(self):
        self.assertEqual(self.iss.created,
                         datetime.datetime(2017, 6, 6, 9, 36, 15))
        self.assertEqual(self.iss.updated,
                         datetime.datetime(2017, 9, 24, 18, 35, 2))

    def test_state(self):
        self.iss.close()
        self.assertEqual(self.iss.state, 'closed')
        self.iss.reopen()
        self.assertEqual(self.iss.state, 'open')

    def test_issue_create(self):
        iss = GitHubIssue.create(self.token,
                                 'gitmate-test-user/test',
                                 'test title', 'test body')
        self.assertEqual(iss.state, 'open')
