import unittest
import os
import datetime

import vcr

from IGitt.GitLab.GitLabIssue import GitLabIssue

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['private_token'],
                 filter_post_data_parameters=['private_token'])


class GitLabIssueTest(unittest.TestCase):

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_issue.yaml',
                         filter_query_parameters=['private_token'])
    def setUp(self):
        self.iss = GitLabIssue(os.environ.get('GITLAB_TEST_TOKEN', ''),
                               'gitmate-test-user/test', 3)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_issue_title.yaml',
                         filter_query_parameters=['private_token'])
    def test_title(self):
        self.assertEqual(self.iss.title, "Don't add mean comments here!")
        self.iss.title = 'new title'
        self.assertEqual(self.iss.title, 'new title')

    def test_url(self):
        self.assertEqual(self.iss.url,
                         'https://gitlab.com/gitmate-test-user/test/issues/3')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_issue_assignee.yaml')
    def test_assignee(self):
        self.assertEqual(self.iss.assignees, tuple())
        iss = GitLabIssue(os.environ.get('GITLAB_TEST_TOKEN', ''),
                          'gitmate-test-user/test', 27)
        iss.assign('meetmangukiya')
        self.assertEqual(iss.assignees, ('meetmangukiya', ))
        iss.unassign('meetmangukiya')
        self.assertEqual(iss.assignees, tuple())

    def test_number(self):
        self.assertEqual(self.iss.number, 3)

    def test_description(self):
        self.assertEqual(self.iss.description,
                         'Stop trying to be badass.')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_issue_add_comment.yaml')
    def test_add_comment(self):
        self.iss.add_comment('this is a test comment')
        self.assertEqual(self.iss.comments[0].body, 'this is a test comment')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_issue_labels.yaml',
                         filter_query_parameters=['private_token'])
    def test_issue_labels(self):
        self.assertEqual(self.iss.labels, set())
        self.iss.labels = self.iss.labels | {'dem'}
        self.assertEqual(len(self.iss.available_labels), 4)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_issue_time.yaml',
                         filter_query_parameters=['private_token'])
    def test_time(self):
        self.assertEqual(self.iss.created,
                         datetime.datetime(2017, 6, 5, 6, 19, 6, 379000))
        self.assertEqual(self.iss.updated,
                         datetime.datetime(2017, 6, 5, 6, 19, 50, 479000))

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_issue_state.yaml',
                         filter_query_parameters=['private_token'])
    def test_state(self):
        self.iss.close()
        self.assertEqual(self.iss.state, 'closed')
        self.iss.reopen()
        self.assertEqual(self.iss.state, 'reopened')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_issue_create_delete.yaml',
                         filter_query_parameters=['private_token'])
    def test_issue_create(self):
        issue = GitLabIssue.create(os.environ.get('GITLAB_TEST_TOKEN', ''),
                                   'gitmate-test-user/test',
                                   'test title', 'test body')
        self.assertEqual(issue.state, 'opened')
        issue.delete()
