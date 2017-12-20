import os

from IGitt.GitHub import GitHubToken, GitHubInstallationToken, GitHubJsonWebToken
from IGitt.GitHub.GitHub import GitHub
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubInstallation import GitHubInstallation
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.Interfaces.Actions import IssueActions, MergeRequestActions, \
    PipelineActions, InstallationActions

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
        self.jwt = GitHubJsonWebToken(os.environ['GITHUB_PRIVATE_KEY'],
                                      int(os.environ['GITHUB_TEST_APP_ID']))
        self.itoken = GitHubInstallationToken(60731, self.jwt)
        self.gh_inst = GitHub(self.itoken)

    def test_unknown_event(self):
        with self.assertRaises(NotImplementedError):
            list(self.gh.handle_webhook('unknown_event', self.default_data))

    def test_installation_deleted_hook(self):
        for event, obj in self.gh_inst.handle_webhook('installation', {
                'installation': {'id': 0},
                'action': 'deleted'
            }):
            self.assertEqual(event, InstallationActions.DELETED)
            self.assertIsInstance(obj[0], GitHubInstallation)

    def test_installation_created_hook(self):
        for event, obj in self.gh_inst.handle_webhook('installation', {
                'installation': {'id': 0},
                'action': 'created',
                'repositories': [
                    {'id': 0, 'full_name': 'star-wars/rogue1'}
                ]
            }):
            inst, repos = obj[0], obj[1]
            self.assertEqual(event, InstallationActions.CREATED)
            self.assertIsInstance(inst, GitHubInstallation)
            self.assertIsInstance(repos[0], GitHubRepository)
            self.assertEqual(repos[0].identifier, 0)
            self.assertEqual(repos[0].full_name, 'star-wars/rogue1')

    def test_installation_repositories_added_hook(self):
        for event, obj in self.gh_inst.handle_webhook('installation_repositories', {
                'action': 'added',
                'installation': {'id': 0},
                'repositories_added': [{
                    'id': 0,
                    'full_name': 'foo/bar'
                }]
            }):
            self.assertEqual(event, InstallationActions.REPOSITORIES_ADDED)
            self.assertIsInstance(obj[0], GitHubInstallation)
            self.assertTrue(all([isinstance(repo, GitHubRepository) for repo in obj[1]]))

    def test_installation_repositories_removed_hook(self):
        for event, obj in self.gh_inst.handle_webhook('installation_repositories', {
                'action': 'removed',
                'installation': {'id': 0},
                'repositories_removed': [{
                    'id': 0,
                    'full_name': 'foo/bar'
                }]
            }):
            self.assertEqual(event, InstallationActions.REPOSITORIES_REMOVED)
            self.assertIsInstance(obj[0], GitHubInstallation)
            self.assertTrue(all([isinstance(repo, GitHubRepository) for repo in obj[1]]))

    def test_issue_hook(self):
        for event, obj in self.gh.handle_webhook('issues', self.default_data):
            self.assertEqual(event, IssueActions.OPENED)
            self.assertIsInstance(obj[0], GitHubIssue)

    def test_pr_hook(self):
        for event, obj in self.gh.handle_webhook('pull_request', self.default_data):
            self.assertEqual(event, MergeRequestActions.OPENED)
            self.assertIsInstance(obj[0], GitHubMergeRequest)

    def test_pr_merge_hook(self):
        data = {**self.default_data, 'action': 'closed'}
        data['pull_request']['merged'] = True
        for event, obj in self.gh.handle_webhook('pull_request', data):
            self.assertEqual(event, MergeRequestActions.MERGED)
            self.assertIsInstance(obj[0], GitHubMergeRequest)

    def test_issue_comment(self):
        for event, obj in self.gh.handle_webhook('issue_comment', self.default_data):
            self.assertEqual(event, IssueActions.COMMENTED)
            self.assertIsInstance(obj[0], GitHubIssue)
            self.assertIsInstance(obj[1], GitHubComment)

    def test_pr_comment(self):
        data = self.default_data
        data['issue']['pull_request'] = {}  # Exists for PRs

        for event, obj in self.gh.handle_webhook('issue_comment', data):
            self.assertEqual(event, MergeRequestActions.COMMENTED)
            self.assertIsInstance(obj[0], GitHubMergeRequest)
            self.assertIsInstance(obj[1], GitHubComment)

    def test_status(self):
        for event, obj in self.gh.handle_webhook('status', self.default_data):
            self.assertEqual(event, PipelineActions.UPDATED)
            self.assertIsInstance(obj[0], GitHubCommit)

    def test_issue_label(self):
        self.default_data.update({
            'label': {'name': 'title'},
            'action': 'labeled',
        })
        for event, obj in self.gh.handle_webhook('issues', self.default_data):
            self.assertEqual(event, IssueActions.LABELED)
            self.assertIsInstance(obj[0], GitHubIssue)
            self.assertEqual(obj[1], 'title')
        self.default_data.update({
            'label': {'name': 'title'},
            'action': 'unlabeled',
        })
        for event, obj in self.gh.handle_webhook('issues', self.default_data):
            self.assertEqual(event, IssueActions.UNLABELED)
            self.assertIsInstance(obj[0], GitHubIssue)
            self.assertEqual(obj[1], 'title')

    def test_pull_request_label(self):
        self.default_data.update({
            'label': {'name': 'title'},
            'action': 'labeled',
        })
        for event, obj in self.gh.handle_webhook('pull_request', self.default_data):
            self.assertEqual(event, MergeRequestActions.LABELED)
            self.assertIsInstance(obj[0], GitHubMergeRequest)
            self.assertEqual(obj[1], 'title')
        self.default_data.update({
            'label': {'name': 'title'},
            'action': 'unlabeled',
        })
        for event, obj in self.gh.handle_webhook('pull_request', self.default_data):
            self.assertEqual(event, MergeRequestActions.UNLABELED)
            self.assertIsInstance(obj[0], GitHubMergeRequest)
            self.assertEqual(obj[1], 'title')

    def test_issue_assignee(self):
        self.default_data.update({
            'assignee': {'login': 'gitmate-bot'},
            'action': 'assigned',
        })
        for event, obj in self.gh.handle_webhook('issues', self.default_data):
            self.assertEqual(event, IssueActions.ASSIGNED)
            self.assertIsInstance(obj[0], GitHubIssue)
            self.assertIsInstance(obj[1], GitHubUser)
            self.assertEqual(obj[1].username, 'gitmate-bot')
        self.default_data.update({
            'assignee': {'login': 'gitmate-bot'},
            'action': 'unassigned',
        })
        for event, obj in self.gh.handle_webhook('issues', self.default_data):
            self.assertEqual(event, IssueActions.UNASSIGNED)
            self.assertIsInstance(obj[0], GitHubIssue)
            self.assertIsInstance(obj[1], GitHubUser)
            self.assertEqual(obj[1].username, 'gitmate-bot')

    def test_pull_request_assignee(self):
        self.default_data.update({
            'assignee': {'login': 'gitmate-bot'},
            'action': 'assigned',
        })
        for event, obj in self.gh.handle_webhook('pull_request', self.default_data):
            self.assertEqual(event, MergeRequestActions.ASSIGNED)
            self.assertIsInstance(obj[0], GitHubMergeRequest)
            self.assertIsInstance(obj[1], GitHubUser)
            self.assertEqual(obj[1].username, 'gitmate-bot')
        self.default_data.update({
            'assignee': {'login': 'gitmate-bot'},
            'action': 'unassigned',
        })
        for event, obj in self.gh.handle_webhook('pull_request', self.default_data):
            self.assertEqual(event, MergeRequestActions.UNASSIGNED)
            self.assertIsInstance(obj[0], GitHubMergeRequest)
            self.assertIsInstance(obj[1], GitHubUser)
            self.assertEqual(obj[1].username, 'gitmate-bot')
