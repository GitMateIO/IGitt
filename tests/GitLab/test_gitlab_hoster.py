import os
import unittest

import vcr

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLab import GitLab
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces.Actions import IssueActions, MergeRequestActions, \
    PipelineActions

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class TestGitLab(unittest.TestCase):

    def setUp(self):
        self.gl = GitLab(GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', '')))

    @my_vcr.use_cassette('tests/GitLab/cassettes/test_gitlab_hoster_master.yaml')
    def test_master_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gl.master_repositories)),
                         ['gitmate-test-user/test'])

    @my_vcr.use_cassette('tests/GitLab/cassettes/test_gitlab_hoster_owned.yaml')
    def test_owned_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gl.owned_repositories)),
                         ['gitmate-test-user/test'])

    @my_vcr.use_cassette('tests/GitLab/cassettes/test_gitlab_hoster_write.yaml')
    def test_write_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gl.write_repositories)),
                         ['gitmate-test-user/test', 'nkprince007/gitmate-test'])

    @my_vcr.use_cassette('tests/GitLab/cassettes/test_gitlab_hoster_get_repo.yaml')
    def test_get_repo(self):
        self.assertEqual(self.gl.get_repo('gitmate-test-user/test').full_name,
                         'gitmate-test-user/test')


class TestGitLabWebhook(unittest.TestCase):

    def setUp(self):
        self.gl = GitLab(GitLabOAuthToken(
            os.environ.get('GITLAB_TEST_TOKEN', '')))
        self.default_data = {
            'project': {
                'path_with_namespace': 'test/test',
            },
            'object_attributes': {
                'id': 12,
                'iid': 23,
                'action': 'open',
                'noteable_type': 'Issue'
            },
            'commit': {
                'id': 'bcbb5ec396a2c0f828686f14fac9b80b780504f2',
            },
            'merge_request': {
                'iid': 123,
            },
            'issue': {
                'iid': 123,
                'action': 'open',
            },
        }

    def test_unknown_event(self):
        with self.assertRaises(NotImplementedError):
            self.gl.handle_webhook('unknown_event', self.default_data)

    def test_issue_hook(self):
        event, obj = self.gl.handle_webhook('Issue Hook', self.default_data)
        self.assertEqual(event, IssueActions.OPENED)
        self.assertIsInstance(obj[0], GitLabIssue)

    def test_pr_hook(self):
        event, obj = self.gl.handle_webhook('Merge Request Hook',
                                            self.default_data)
        self.assertEqual(event, MergeRequestActions.OPENED)
        self.assertIsInstance(obj[0], GitLabMergeRequest)

    def test_pr_synchronized(self):
        data = self.default_data
        data['object_attributes']['oldrev'] = 'deadbeef'
        event, obj = self.gl.handle_webhook('Merge Request Hook',
                                            self.default_data)
        self.assertEqual(event, MergeRequestActions.SYNCHRONIZED)
        self.assertIsInstance(obj[0], GitLabMergeRequest)

    def test_issue_comment(self):
        event, obj = self.gl.handle_webhook('Note Hook', self.default_data)
        self.assertEqual(event, IssueActions.COMMENTED)
        self.assertIsInstance(obj[0], GitLabIssue)
        self.assertIsInstance(obj[1], GitLabComment)

    def test_unsupported_comment(self):
        data = self.default_data
        data['object_attributes']['noteable_type'] = 'Snippet'

        with self.assertRaises(NotImplementedError):
            self.gl.handle_webhook('Note Hook', data)

    def test_pr_comment(self):
        data = self.default_data
        data['object_attributes']['noteable_type'] = 'MergeRequest'

        event, obj = self.gl.handle_webhook('Note Hook', data)
        self.assertEqual(event, MergeRequestActions.COMMENTED)
        self.assertIsInstance(obj[0], GitLabMergeRequest)
        self.assertIsInstance(obj[1], GitLabComment)

    def test_status(self):
        event, obj = self.gl.handle_webhook('Pipeline Hook', self.default_data)
        self.assertEqual(event, PipelineActions.UPDATED)
        self.assertIsInstance(obj[0], GitLabCommit)
