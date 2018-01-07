import os

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLab import GitLab
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces.Actions import IssueActions, MergeRequestActions, \
    PipelineActions

from tests import IGittTestCase


class GitLabHosterTest(IGittTestCase):

    def setUp(self):
        self.gl = GitLab(GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', '')))

    def test_repo_permissions_inheritance(self):
        repos = [
            {
                'namespace':{'id': 1, 'parent_id': None},
                'permissions': {'group_access': {'access_level': 40},
                                'project_access': None}
            },
            {
                'namespace': {'id': 2, 'parent_id': 1},
                'permissions': {'group_access': None, 'project_access': None}
            },
            {
                'namespace': {'id': 3, 'parent_id': 2},
                'permissions': {'group_access': None, 'project_access': None}
            },
            {
                'namespace': {'id': 4, 'parent_id': None},
                'permissions': {'group_access': None,
                                'project_access': {'access_level': 40}}
            }
        ]
        self.assertEqual(set(map(lambda x: x['namespace']['id'],
                                 GitLab._get_repos_with_permissions(
                                     repos, AccessLevel.ADMIN))),
                         {1, 2, 3, 4})

    def test_master_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gl.master_repositories)),
                         ['gitmate-test-user/test'])

    def test_owned_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gl.owned_repositories)),
                         ['gitmate-test-user/test'])

    def test_write_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gl.write_repositories)),
                         ['gitmate-test-user/test'])

    def test_get_repo(self):
        self.assertEqual(self.gl.get_repo('gitmate-test-user/test').full_name,
                         'gitmate-test-user/test')


class GitLabWebhookTest(IGittTestCase):

    def setUp(self):
        self.gl = GitLab(GitLabOAuthToken(
            os.environ.get('GITLAB_TEST_TOKEN', '')))
        self.repo_name = 'test/test'
        self.default_data = {
            'project': {
                'path_with_namespace': self.repo_name,
            },
            'object_attributes': {
                'id': 12,
                'iid': 23,
                'action': 'open',
                'noteable_type': 'Issue',
                'target': {
                    'path_with_namespace': 'gitmate-test-user/test'
                }
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
            'repository': {
                'git_ssh_url': 'git@gitlab.com:gitmate-test-user/test.git'
            }
        }

    def test_unknown_event(self):
        with self.assertRaises(NotImplementedError):
            list(self.gl.handle_webhook('unknown_event', self.default_data))

    def test_issue_hook(self):
        for event, obj in self.gl.handle_webhook('Issue Hook',
                                                 self.default_data):
            self.assertEqual(event, IssueActions.OPENED)
            self.assertIsInstance(obj[0], GitLabIssue)

    def test_pr_hook(self):
        for event, obj in self.gl.handle_webhook('Merge Request Hook',
                                                 self.default_data):
            self.assertEqual(event, MergeRequestActions.OPENED)
            self.assertIsInstance(obj[0], GitLabMergeRequest)

    def test_pr_synchronized(self):
        data = self.default_data
        data['object_attributes']['oldrev'] = 'deadbeef'
        for event, obj in self.gl.handle_webhook('Merge Request Hook',
                                                 self.default_data):
            self.assertEqual(event, MergeRequestActions.SYNCHRONIZED)
            self.assertIsInstance(obj[0], GitLabMergeRequest)

    def test_issue_comment(self):
        for event, obj in self.gl.handle_webhook('Note Hook',
                                                 self.default_data):
            self.assertEqual(event, IssueActions.COMMENTED)
            self.assertIsInstance(obj[0], GitLabIssue)
            self.assertIsInstance(obj[1], GitLabComment)

    def test_unsupported_comment(self):
        data = self.default_data
        data['object_attributes']['noteable_type'] = 'Snippet'

        with self.assertRaises(NotImplementedError):
            list(self.gl.handle_webhook('Note Hook', data))

    def test_pr_comment(self):
        data = self.default_data
        del data['project']
        data['object_attributes']['noteable_type'] = 'MergeRequest'

        for event, obj in self.gl.handle_webhook('Note Hook', data):
            self.assertEqual(event, MergeRequestActions.COMMENTED)
            self.assertIsInstance(obj[0], GitLabMergeRequest)
            self.assertIsInstance(obj[1], GitLabComment)

    def test_status(self):
        del self.default_data['project']
        del self.default_data['object_attributes']
        for event, obj in self.gl.handle_webhook('Pipeline Hook',
                                                 self.default_data):
            self.assertEqual(event, PipelineActions.UPDATED)
            self.assertIsInstance(obj[0], GitLabCommit)

    def test_issue_label(self):
        obj_attrs = self.default_data['object_attributes']
        obj_attrs.update({'action': 'update'})

        self.default_data.update({
            'object_attributes': obj_attrs,
            'changes': {
                'labels': {
                    'previous': [{'title': 'old'}, {'title': 'old2'}],
                    'current': [{'title': 'new'}],
                },
            },
        })

        unlabeled_labels = set()
        labeled_labels = set()
        for event, obj in self.gl.handle_webhook('Issue Hook',
                                                 self.default_data):
            self.assertIsInstance(obj[0], GitLabIssue)
            if event == IssueActions.LABELED:
                labeled_labels.add(obj[1])
            elif event == IssueActions.UNLABELED:
                unlabeled_labels.add(obj[1])

        self.assertEqual(unlabeled_labels, {'old', 'old2'})
        self.assertEqual(labeled_labels, {'new'})

    def test_merge_request_label(self):
        obj_attrs = self.default_data['object_attributes']
        obj_attrs.update({'action': 'update'})

        self.default_data.update({
            'object_attributes': obj_attrs,
            'changes': {
                'labels': {
                    'previous': [{'title': 'old'}, {'title': 'old2'}],
                    'current': [{'title': 'new'}],
                },
            },
        })

        unlabeled_labels = set()
        labeled_labels = set()
        for event, obj in self.gl.handle_webhook('Merge Request Hook',
                                                 self.default_data):
            self.assertIsInstance(obj[0], GitLabMergeRequest)
            if event == MergeRequestActions.LABELED:
                labeled_labels.add(obj[1])
            elif event == MergeRequestActions.UNLABELED:
                unlabeled_labels.add(obj[1])

        self.assertEqual(unlabeled_labels, {'old', 'old2'})
        self.assertEqual(labeled_labels, {'new'})
