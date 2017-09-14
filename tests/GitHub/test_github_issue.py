import unittest
import os
import datetime

import vcr

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubIssue import GitHubIssue

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class GitHubIssueTest(unittest.TestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.iss = GitHubIssue(self.token,
                               'gitmate-test-user/test', 39)

    def test_repo(self):
        self.assertEqual(self.iss.repository.full_name,
                         'gitmate-test-user/test')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_issue_title.yaml',
                         filter_query_parameters=['access_token'])
    def test_title(self):
        self.iss.title = 'new title'
        self.assertEqual(self.iss.title, 'new title')

    def test_url(self):
        self.assertEqual(self.iss.url,
                         'https://github.com/gitmate-test-user/test/issues/39')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_issue_assignee.yaml')
    def test_assignee(self):
        self.assertEqual(self.iss.assignees, tuple())
        iss = GitHubIssue(self.token,
                          'gitmate-test-user/test', 41)
        iss.assign('meetmangukiya')
        self.assertEqual(iss.assignees, ('meetmangukiya', ))
        iss.unassign('meetmangukiya')
        self.assertEqual(iss.assignees, tuple())
        iss = GitHubIssue(self.token, 'gitmate-test-user/test', 107)
        self.assertEqual(iss.assignees, tuple())

    def test_number(self):
        self.assertEqual(self.iss.number, 39)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_issue_desc.yaml',
                         filter_query_parameters=['access_token'])
    def test_description(self):
        self.assertEqual(self.iss.description, 'test description\r\n')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_issue_auth.yaml',
                         filter_query_parameters=['access_token'])
    def test_author(self):
        self.assertEqual(self.iss.author, 'meetmangukiya')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_issue_comment.yaml',
                         filter_query_parameters=['access_token'])
    def test_comment(self):
        self.iss.add_comment('this is a comment')
        self.assertEqual(self.iss.comments[0].body, 'this is a comment')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_issue_labels.yaml',
                         filter_query_parameters=['access_token'])
    def test_issue_labels(self):
        self.assertEqual(list(self.iss.labels), [])
        self.iss.labels = self.iss.labels | {'dem'}
        self.iss.labels = self.iss.labels  # Doesn't do a request :)
        self.assertEqual(len(self.iss.available_labels), 4)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_issue_time.yaml',
                         filter_query_parameters=['access_token'])
    def test_time(self):
        self.assertEqual(self.iss.created,
                         datetime.datetime(2017, 6, 6, 9, 36, 15))
        self.assertEqual(self.iss.updated,
                         datetime.datetime(2017, 6, 13, 11, 59, 56))

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_issue_state.yaml',
                         filter_query_parameters=['access_token'])
    def test_state(self):
        self.iss.close()
        self.assertEqual(self.iss.state, 'closed')
        self.iss.reopen()
        self.assertEqual(self.iss.state, 'open')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_issue_create.yaml',
                         filter_query_parameters=['access_token'])
    def test_issue_create(self):
        iss = GitHubIssue.create(self.token,
                                 'gitmate-test-user/test',
                                 'test title', 'test body')
        self.assertEqual(iss.state, 'open')
