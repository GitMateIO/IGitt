import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubCommit import GitHubCommit, get_diff_index
from IGitt.Interfaces.CommitStatus import CommitStatus, Status

from tests import IGittTestCase


class GitHubCommitTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.commit = GitHubCommit(self.token,
                                   'gitmate-test-user/test',
                                   '645961c0841a84c1dd2a58535aa70ad45be48c46')

    def test_sha(self):
        self.assertIn('645961c', self.commit.sha)

    def test_message(self):
        self.assertEqual(self.commit.message, 'Updated README.md')

    def test_repository(self):
        self.assertEqual(self.commit.repository.full_name,
                         'gitmate-test-user/test')

    def test_parent(self):
        self.assertEqual(self.commit.parent.sha,
                         '674498fd415cfadc35c5eb28b8951e800f357c6f')

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

    def test_combined_status(self):
        self.assertEqual(self.commit.combined_status, Status.PENDING)

    def test_get_patch_for_file(self):
        patch = self.commit.get_patch_for_file('README.md')
        self.assertEqual(patch,
                         '@@ -1,2 +1,4 @@\n # test\n a test repo\n+\n+yeah thats it')

    def test_comment(self):
        commit = GitHubCommit(self.token, 'gitmate-test-user/test',
                              'f6d2b7c66372236a090a2a74df2e47f42a54456b')
        self.assertIn('An issue is here',
                      commit.comment('An issue is here').body)

        self.assertIn("Here in line 4, there's a spelling mistake",
                      commit.comment("Here in line 4, there's a spelling mistake!",
                                     'README.md', 4).body)
        self.assertIn("Here in line 4, there's a spelling mistake!",
                      commit.comment("Here in line 4, there's a spelling mistake!",
                                     'README.md', 4, mr_number=7).body)
        self.assertIn('test comment',
                      commit.comment('test comment', 'READNOT.md', mr_number=7).body)
        self.assertIn('test comment',
                      commit.comment('test comment', 'READNOT.md', 4).body)

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

    def test_unified_diff(self):
        self.assertEqual(self.commit.unified_diff,
                         '--- a/README.md\n'
                         '+++ b/README.md\n'
                         '@@ -1,2 +1,4 @@\n'
                         ' # test\n'
                         ' a test repo\n'
                         '+\n'
                         '+yeah thats it')
