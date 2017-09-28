import os
import datetime

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest

from tests import IGittTestCase


class GitLabMergeRequestTest(IGittTestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.mr = GitLabMergeRequest(self.token, 'gitmate-test-user/test', 7)

    def test_base(self):
        self.assertEqual(self.mr.base.sha,
                         '7747ee49b7d322e7d82520126ca275115aa67447')

    def test_head(self):
        self.assertEqual(self.mr.head.sha,
                         'f6d2b7c66372236a090a2a74df2e47f42a54456b')
        # test for forks
        mr = GitLabMergeRequest(self.token, 'gitmate-test-user/test', 26)
        self.assertEqual(mr.head.sha, '33c53a63131beb1b06c10c4d3b2d7591338dbaa0')
        # GitLab doesn't copy the commit to the base repo
        self.assertEqual(mr.head.repository.full_name, 'nkprince007/test')

    def test_base_branch_name(self):
        self.assertEqual(self.mr.base_branch_name, 'master')

    def test_head_branch_name(self):
        self.assertEqual(self.mr.head_branch_name, 'gitmate-test-user-patch-2')

    def test_commits(self):
        self.assertEqual([commit.sha for commit in self.mr.commits],
                         ['f6d2b7c66372236a090a2a74df2e47f42a54456b'])

    def test_repository(self):
        self.assertEqual(self.mr.target_repository.full_name,
                         'gitmate-test-user/test')
        self.assertEqual(self.mr.source_repository.full_name,
                         'gitmate-test-user/test')

    def test_diffstat(self):
        self.assertEqual(self.mr.diffstat, (2, 0))
        mr = GitLabMergeRequest(self.token, 'gitmate-test-user/test', 39)
        self.assertEqual(mr.diffstat, (0, 0))

    def test_time(self):
        self.assertEqual(self.mr.created, datetime.datetime(
            2017, 6, 7, 12, 1, 20, 476000))
        self.assertEqual(self.mr.updated, datetime.datetime(
            2017, 9, 24, 17, 45, 50, 540000))

    def test_affected_files(self):
        self.assertEqual(self.mr.affected_files, {'README.md'})

    def test_number(self):
        self.assertEqual(self.mr.number, 7)

    def test_url(self):
        self.assertEqual(self.mr.url,
                         'https://gitlab.com/gitmate-test-user/test/merge_requests/7')

    def test_change_state(self):
        self.mr.close()
        self.assertEqual(self.mr.state, 'closed')
        self.mr.reopen()
        self.assertEqual(self.mr.state, 'opened')

    def test_closes_issues(self):
        mr = GitLabMergeRequest(self.token, 'gitmate-test-user/test', 25)
        self.assertEqual({int(issue.number) for issue in mr.closes_issues},
                         {21, 22, 23, 26, 27, 30})

    def test_assignees(self):
        # test merge request with no assignees
        mr = GitLabMergeRequest(self.token, 'gitmate-test-user/test', 25)
        self.assertEqual(mr.assignees, set())
