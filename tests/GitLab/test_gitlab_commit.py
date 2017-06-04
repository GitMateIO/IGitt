import os
import unittest

import vcr

from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.Interfaces.CommitStatus import CommitStatus, Status

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['private_token'],
                 filter_post_data_parameters=['private_token'],
                 filter_headers=['Link'])


class GitLabCommitTest(unittest.TestCase):

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_commit.yaml')
    def setUp(self):
        self.commit = GitLabCommit(os.environ.get('GITLAB_TEST_TOKEN', ''),
                                   'gitmate-test-user/test', '3fc4b86')

    def test_sha(self):
        self.assertIn('3fc4b86', self.commit.sha)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_commit_repository.yaml')
    def test_repository(self):
        self.assertEqual(self.commit.repository.full_name,
                         'gitmate-test-user/test')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_commit_parent.yaml')
    def test_parent(self):
        self.assertEqual(self.commit.parent.sha,
                         '674498fd415cfadc35c5eb28b8951e800f357c6f')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_commit_status.yaml')
    def test_set_status(self):
        self.commit = GitLabCommit(os.environ.get('GITLAB_TEST_TOKEN', ''),
                                   'gitmate-test-user/test', '3fc4b86')
        status = CommitStatus(Status.FAILED, 'Theres a problem',
                              'gitmate/test')
        self.commit.set_status(status)
        self.assertEqual(self.commit.get_statuses(
            ).pop().description, 'Theres a problem')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_commit_get_patch.yaml')
    def test_get_patch_for_file(self):
        patch = self.commit.get_patch_for_file('README.md')
        self.assertEqual(patch, '--- a/README.md\n'
                                '+++ b/README.md\n'
                                '@@ -1,2 +1,4 @@\n'
                                ' # test\n'
                                ' a test repo\n'
                                '+\n'
                                '+a tst pr\n')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_commit_comment.yaml')
    def test_comment(self):
        self.commit = GitLabCommit(os.environ.get('GITLAB_TEST_TOKEN', ''),
                                   'gitmate-test-user/test', '3fc4b86')
        self.commit.comment('An issue is here')
        self.commit.comment("Here in line 4, there's a spelling mistake!",
                            'README.md', 4)
        self.commit.comment("Here in line 4, there's a spelling mistake!",
                            'README.md', 4, mr_number=6)
        self.commit.comment('test comment', 'READNOT.md', mr_number=6)
        self.commit.comment('test comment', 'READNOT.md', 4)
