import unittest
import os
import datetime

import vcr

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class TestGitLabMergeRequest(unittest.TestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.mr = GitLabMergeRequest(self.token, 'gitmate-test-user/test', 7)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_base.yaml')
    def test_base(self):
        self.assertEqual(self.mr.base.sha,
                         '198dd16f8249ea98ed41876efe27d068b69fa215')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_head.yaml')
    def test_head(self):
        self.assertEqual(self.mr.head.sha,
                         'f6d2b7c66372236a090a2a74df2e47f42a54456b')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_basebranchname.yaml')
    def test_base_branch_name(self):
        self.assertEqual(self.mr.base_branch_name, 'master')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_headbranchname.yaml')
    def test_head_branch_name(self):
        self.assertEqual(self.mr.head_branch_name, 'gitmate-test-user-patch-2')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_commits.yaml')
    def test_commits(self):
        self.assertEqual([commit.sha for commit in self.mr.commits],
                         ['f6d2b7c66372236a090a2a74df2e47f42a54456b'])

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_repository.yaml')
    def test_repository(self):
        self.assertEqual(self.mr.repository.full_name,
                         'gitmate-test-user/test')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_diffstat.yaml')
    def test_diffstat(self):
        self.assertEqual(self.mr.diffstat, (2, 0))

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_time.yaml')
    def test_time(self):
        self.assertEqual(self.mr.created, datetime.datetime(
            2017, 6, 7, 12, 1, 20, 476000))
        self.assertEqual(self.mr.updated, datetime.datetime(
            2017, 6, 9, 9, 49, 7, 691000))

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_affected_files.yaml')
    def test_affected_files(self):
        self.assertEqual(self.mr.affected_files, {'README.md'})

    def test_number(self):
        self.assertEqual(self.mr.number, 7)

    def test_url(self):
        self.assertEqual(self.mr.url,
                         'https://gitlab.com/gitmate-test-user/test/merge_requests/7')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_states.yaml')
    def test_change_state(self):
        self.mr.close()
        self.assertEqual(self.mr.state, 'closed')
        self.mr.reopen()
        self.assertEqual(self.mr.state, 'reopened')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_closes_issues.yaml')
    def test_closes_issues(self):
        mr = GitLabMergeRequest(self.token, 'gitmate-test-user/test', 25)
        self.assertEqual({int(issue.number) for issue in mr.closes_issues},
                         {21, 22, 23, 26, 27, 30})

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_mergeable.yaml')
    def test_mergeable(self):
        mr = GitLabMergeRequest(self.token, 'gitmate-test-user/test', 7)
        self.assertFalse(mr.mergeable)
        mr = GitLabMergeRequest(self.token, 'gitmate-test-user/test', 27)
        self.assertTrue(mr.mergeable)
