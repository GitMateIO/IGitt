import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHub import GitHub
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.Interfaces.Actions import IssueActions, MergeRequestActions, \
    PipelineActions

from tests import IGittTestCase


class GitHubHosterTest(IGittTestCase):

    def setUp(self):
        self.gh = GitHub(GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', '')))

    def test_master_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gh.master_repositories)),
                         ['GitMateIO/gitmate-2',
                          'GitMateIO/gitmate-2-frontend',
                          'gitmate-test-user/empty',
                          'gitmate-test-user/test'])

    def test_owned_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gh.owned_repositories)),
                         ['gitmate-test-user/empty', 'gitmate-test-user/test'])

    def test_write_repositories(self):
        self.assertEqual(sorted(map(lambda x: x.full_name, self.gh.write_repositories)),
                         ['GitMateIO/IGitt',
                          'GitMateIO/gitmate-2',
                          'GitMateIO/gitmate-2-frontend',
                          'gitmate-test-user/empty',
                          'gitmate-test-user/test',
                          'sils/gitmate-test'])

    def test_get_repo(self):
        self.assertEqual(self.gh.get_repo('gitmate-test-user/test').full_name,
                         'gitmate-test-user/test')


class TestGitHubWebhook(IGittTestCase):

    def setUp(self):
        self.gh = GitHub(GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', '')))
        self.repo_name = 'org/test_repo'
        self.default_data = {
            'repository': {
                'full_name': self.repo_name
            },
            'pull_request': {'number': 0},
            'issue': {'number': 0},
            'action': 'opened',
            'comment': {
                'id': 1,
            },
            'commit': {
                'sha': 'deadbeef',
            }
        }

    def test_unknown_event(self):
        with self.assertRaises(NotImplementedError):
            self.gh.handle_webhook(self.repo_name,
                                   'unknown_event',
                                   self.default_data)

    def test_issue_hook(self):
        event, obj = self.gh.handle_webhook(
            self.repo_name, 'issues', self.default_data)
        self.assertEqual(event, IssueActions.OPENED)
        self.assertIsInstance(obj[0], GitHubIssue)

    def test_pr_hook(self):
        event, obj = self.gh.handle_webhook(
            self.repo_name, 'pull_request', self.default_data)
        self.assertEqual(event, MergeRequestActions.OPENED)
        self.assertIsInstance(obj[0], GitHubMergeRequest)

    def test_pr_merge_hook(self):
        data = {**self.default_data, 'action': 'closed'}
        data['pull_request']['merged'] = True
        event, obj = self.gh.handle_webhook(
            self.repo_name, 'pull_request', data)
        self.assertEqual(event, MergeRequestActions.MERGED)
        self.assertIsInstance(obj[0], GitHubMergeRequest)

    def test_issue_comment(self):
        event, obj = self.gh.handle_webhook(
            self.repo_name, 'issue_comment', self.default_data)
        self.assertEqual(event, IssueActions.COMMENTED)
        self.assertIsInstance(obj[0], GitHubIssue)
        self.assertIsInstance(obj[1], GitHubComment)

    def test_pr_comment(self):
        data = self.default_data
        data['issue']['pull_request'] = {}  # Exists for PRs

        event, obj = self.gh.handle_webhook(
            self.repo_name, 'issue_comment', data)
        self.assertEqual(event, MergeRequestActions.COMMENTED)
        self.assertIsInstance(obj[0], GitHubMergeRequest)
        self.assertIsInstance(obj[1], GitHubComment)

    def test_status(self):
        event, obj = self.gh.handle_webhook(
            self.repo_name, 'status', self.default_data)
        self.assertEqual(event, PipelineActions.UPDATED)
        self.assertIsInstance(obj[0], GitHubCommit)
