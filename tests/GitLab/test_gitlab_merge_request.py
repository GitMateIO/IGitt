import unittest
import os
import datetime

import vcr

from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['private_token'],
                 filter_post_data_parameters=['private_token'])


class TestGitLabMergeRequest(unittest.TestCase):

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request.yaml')
    def setUp(self):
        self.mr = GitLabMergeRequest(os.environ.get('GITLAB_TEST_TOKEN', ''),
                                     'gitmate-test-user/test',
                                     7)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_base.yaml')
    def test_base(self):
        self.assertEqual(self.mr.base.sha,
                         '198dd16f8249ea98ed41876efe27d068b69fa215')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_head.yaml')
    def test_head(self):
        self.assertEqual(self.mr.head.sha,
                         'f6d2b7c66372236a090a2a74df2e47f42a54456b')

    def test_base_branch_name(self):
        self.assertEqual(self.mr.base_branch_name, 'master')

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

    def test_time(self):
        self.assertEqual(self.mr.created, datetime.datetime(
            2017, 6, 7, 12, 1, 20, 476000))
        self.assertEqual(self.mr.updated, datetime.datetime(
            2017, 6, 8, 14, 53, 58, 726000))

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_affected_files.yaml')
    def test_affected_files(self):
        self.assertEqual(self.mr.affected_files, {'README.md'})

    def test_number(self):
        self.assertEqual(self.mr.number, 7)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_merge_request_states.yaml')
    def test_change_state(self):
        self.mr.close()
        self.assertEqual(self.mr.state, 'closed')
        self.mr.reopen()
        self.assertEqual(self.mr.state, 'reopened')
