import os
import datetime

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.Interfaces.MergeRequest import MergeRequestStates

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
        self.mr.description = 'changed description'
        self.assertEqual(self.mr.description, 'changed description')

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
            2017, 10, 18, 8, 34, 21))

    def test_affected_files(self):
        self.assertEqual(self.mr.affected_files, {'README.md'})

    def test_number(self):
        self.assertEqual(self.mr.number, 7)

    def test_url(self):
        self.assertEqual(self.mr.url,
                         'https://api.github.com/repos/gitmate-test-user/test/issues/7')

    def test_web_url(self):
        self.assertEqual(self.mr.web_url,
                         'https://github.com/gitmate-test-user/test/pull/7')

    def test_change_state(self):
        self.mr.close()
        self.assertEqual(self.mr.state, MergeRequestStates.CLOSED)
        self.mr.reopen()
        self.assertEqual(self.mr.state, MergeRequestStates.OPEN)

    def test_closes_issues(self):
        mr = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 113)
        self.assertEqual({int(issue.number) for issue in mr.closes_issues},
                         {98, 104, 1, 107, 97, 105})

    def test_mentioned_issues(self):
        mr = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 96)
        self.assertEqual({int(issue.number) for issue in mr.mentioned_issues},
                         {114, 115, 127})

    def test_tests_passed(self):
        self.assertEqual(self.mr.tests_passed, True)
        mr = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 6)
        self.assertEqual(mr.tests_passed, False)

    def test_assignees(self):
        # test merge request with no assignees
        self.assertEqual(self.mr.assignees, set())

    def test_author(self):
        self.assertEqual(self.mr.author.username, 'gitmate-test-user')

    def test_state(self):
        merged = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 130)
        closed = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 129)
        opened = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 126)
        self.assertEqual(merged.state, MergeRequestStates.MERGED)
        self.assertEqual(closed.state, MergeRequestStates.CLOSED)
        self.assertEqual(opened.state, MergeRequestStates.OPEN)

    def test_merge_empty(self):
        mr = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 133)
        mr.merge()
        self.assertEqual(mr.state, MergeRequestStates.MERGED)

    def test_merge_params(self):
        commit_msg = 'Test commit title\n\nTest commit body'
        head_sha = 'fd2e00646b19fc93e72992761c0b2ef31fe697ae'
        method = 'squash'
        mr = GitHubMergeRequest(self.token, 'gitmate-test-user/test', 134)
        mr.merge(message=commit_msg, sha=head_sha, _github_merge_method=method)
        self.assertEqual(mr.state, MergeRequestStates.MERGED)
