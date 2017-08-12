import os
import unittest

import vcr

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubCommit import GitHubCommit, get_diff_index
from IGitt.Interfaces.CommitStatus import CommitStatus, Status

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'],
                 filter_headers=['Link'])


class GitHubCommitTest(unittest.TestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.commit = GitHubCommit(self.token,
                                   'gitmate-test-user/test',
                                   '645961c0841a84c1dd2a58535aa70ad45be48c46')

    def test_sha(self):
        self.assertIn('645961c', self.commit.sha)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_commit_message.yaml')
    def test_message(self):
        self.assertEqual(self.commit.message, 'Updated README.md')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_commit_repository.yaml')
    def test_repository(self):
        self.assertEqual(self.commit.repository.full_name,
                         'gitmate-test-user/test')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_commit_parent.yaml')
    def test_parent(self):
        self.assertEqual(self.commit.parent.sha,
                         '674498fd415cfadc35c5eb28b8951e800f357c6f')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_commit_status.yaml')
    def test_set_status(self):
        self.commit = GitHubCommit(self.token,
                                   'gitmate-test-user/test',
                                   '3fc4b860e0a2c17819934d678decacd914271e5c')
        status = CommitStatus(Status.FAILED, 'Theres a problem',
                              'gitmate/test')
        self.commit.set_status(status)
        self.assertIn('Theres a problem',
                      [status.description
                       for status in self.commit.get_statuses()])

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_combined_commit_status.yaml')
    def test_combined_status(self):
        self.assertEqual(self.commit.combined_status, Status.PENDING)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_commit_get_patch.yaml')
    def test_get_patch_for_file(self):
        patch = self.commit.get_patch_for_file('README.md')
        self.assertEqual(patch,
                         '@@ -1,2 +1,4 @@\n # test\n a test repo\n+\n+yeah thats it')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_commit_comment.yaml')
    def test_comment(self):
        self.commit = GitHubCommit(self.token,
                                   'gitmate-test-user/test', '3fc4b86')
        self.commit.comment('An issue is here')
        self.commit.comment("Here in line 4, there's a spelling mistake!",
                            'README.md', 4)
        self.commit.comment("Here in line 4, there's a spelling mistake!",
                            'README.md', 4, mr_number=6)
        self.commit.comment('test comment', 'READNOT.md', mr_number=6)
        self.commit.comment('test comment', 'READNOT.md', 4)

    def test_get_diff_index(self):
        patch = ('---/version/a\n'
                 '+++/version/b\n'
                 '@@ -1,2 +1,4 @@\n'
                 ' # test\n'  # Line 1
                 '+\n'  # Line 2
                 '-a test repo\n'  # Line 3
                 '+something new\n'  # Line 3
                 ' something old\n')  # Line 4
        self.assertEqual(get_diff_index(patch, 1), 1)
        self.assertEqual(get_diff_index(patch, 8), None)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_commit_unified_diff.yaml')
    def test_unified_diff(self):
        self.assertEqual(self.commit.unified_diff,
                         '--- a/README.md\n'
                         '+++ b/README.md\n'
                         '@@ -1,2 +1,4 @@\n'
                         ' # test\n'
                         ' a test repo\n'
                         '+\n'
                         '+yeah thats it')
