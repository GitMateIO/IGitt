import os
import datetime

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest

from tests import IGittTestCase


class GitHubMergeRequestTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.mr = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 7)

    def test_base(self):
        self.assertEqual(self.mr.base.sha,
                         '674498fd415cfadc35c5eb28b8951e800f357c6f')

    def test_head(self):
        self.assertEqual(self.mr.head.sha,
                         'f6d2b7c66372236a090a2a74df2e47f42a54456b')
        # test for forks
        mr = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 113)
        self.assertEqual(mr.head.sha, 'fb37d69e72b46a52f8694cf45adb007315de3b6e')
        # GitHub copies commit to the base repo
        self.assertEqual(mr.head.repository.full_name, 'gitmate-test-user/test')

    def test_description(self):
        self.assertEqual(self.mr.description, '')

    def test_title(self):
        self.mr.title = 'changed title'
        self.assertEqual(self.mr.title, 'changed title')

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

    def test_time(self):
        self.assertEqual(self.mr.created, datetime.datetime(
            2016, 1, 24, 19, 47, 19))
        self.assertEqual(self.mr.updated, datetime.datetime(
            2017, 9, 24, 18, 39, 2))

    def test_affected_files(self):
        self.assertEqual(self.mr.affected_files, {'README.md'})

    def test_number(self):
        self.assertEqual(self.mr.number, 7)

    def test_url(self):
        self.assertEqual(self.mr.url,
                         'https://github.com/gitmate-test-user/test/pull/7')

    def test_change_state(self):
        self.mr.close()
        self.assertEqual(self.mr.state, 'closed')
        self.mr.reopen()
        self.assertEqual(self.mr.state, 'open')

    def test_closes_issues(self):
        mr = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 113)
        self.assertEqual({int(issue.number) for issue in mr.closes_issues},
                         {98, 104, 1, 107, 97, 105})

    def test_tests_passed(self):
        self.assertEqual(self.mr.tests_passed, True)
        mr = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 6)
        self.assertEqual(mr.tests_passed, False)

    def test_assignees(self):
        # test merge request with no assignees
        self.assertEqual(self.mr.assignees, set())
