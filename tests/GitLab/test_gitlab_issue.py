import os
import datetime

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabIssue import GitLabIssue

from tests import IGittTestCase


class GitLabIssueTest(IGittTestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.iss = GitLabIssue(self.token,
                               'gitmate-test-user/test', 3)

    def test_repo(self):
        self.assertEqual(self.iss.repository.full_name,
                         'gitmate-test-user/test')

    def test_title(self):
        self.iss.title = 'new title'
        self.assertEqual(self.iss.title, 'new title')

    def test_assignee(self):
        self.assertEqual(self.iss.assignees, set())
        iss = GitLabIssue(self.token,
                          'gitmate-test-user/test', 27)
        iss.assign('meetmangukiya')
        self.assertEqual(iss.assignees, {'meetmangukiya'})
        iss.unassign('meetmangukiya')
        self.assertEqual(iss.assignees, set())
        iss = GitLabIssue(self.token, 'gitmate-test-user/test', 2)
        self.assertEqual(iss.assignees, set())

    def test_number(self):
        self.assertEqual(self.iss.number, 3)

    def test_description(self):
        self.assertEqual(self.iss.description,
                         'Stop trying to be badass.')

    def test_author(self):
        self.assertEqual(self.iss.author, 'gitmate-test-user')

    def test_add_comment(self):
        self.iss.add_comment('this is a test comment')
        self.assertEqual(self.iss.comments[0].body, 'this is a test comment')

    def test_issue_labels(self):
        self.iss.labels = set()
        self.assertEqual(self.iss.labels, set())
        self.iss.labels = self.iss.labels | {'dem'}
        self.iss.labels = self.iss.labels  # Doesn't do a request :)
        self.assertEqual(len(self.iss.available_labels), 4)
        self.assertEqual(len(self.iss.labels), 1)

    def test_time(self):
        self.assertEqual(self.iss.created,
                         datetime.datetime(2017, 6, 5, 6, 19, 6, 379000))
        self.assertEqual(self.iss.updated,
                         datetime.datetime(2017, 9, 24, 17, 6, 45, 955000))

    def test_state(self):
        self.iss.close()
        self.assertEqual(self.iss.state, 'closed')
        self.iss.reopen()
        self.assertEqual(self.iss.state, 'opened')

    def test_issue_create(self):
        issue = GitLabIssue.create(self.token,
                                   'gitmate-test-user/test',
                                   'test title', 'test body')
        self.assertEqual(issue.state, 'opened')
        issue.delete()

    def test_description_is_string(self):
        issue = GitLabIssue(self.token, 'gitmate-test-user/test', 23)
        issue.data['description'] = None
        self.assertEqual(issue.description, '')
