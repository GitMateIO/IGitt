import os

from IGitt.GitHub import GitHubJsonWebToken
from IGitt.GitHub import GitHubInstallationToken
from IGitt.GitHub.GitHubInstallation import GitHubInstallation

from tests import IGittTestCase


class GitHubInstallationTest(IGittTestCase):
    def setUp(self):
        self.token = GitHubJsonWebToken(os.environ['GITHUB_PRIVATE_KEY'],
                                        int(os.environ['GITHUB_TEST_APP_ID']))
        self.itoken = GitHubInstallationToken(57250, self.token)
        self.installation = GitHubInstallation(self.itoken, 57250)

    def test_id(self):
        self.assertEqual(self.installation.identifier, 57250)

    def test_app_id(self):
        self.assertEqual(self.installation.app_id,
                         int(os.environ['GITHUB_TEST_APP_ID']))

    def test_webhooks(self):
        self.assertEqual(self.installation.webhooks,
                         ['issues',
                          'issue_comment',
                          'public',
                          'pull_request',
                          'pull_request_review',
                          'pull_request_review_comment',
                          'push',
                          'repository',
                          'status'])

    def test_permissions(self):
        self.assertEqual(self.installation.permissions,
                         {'administration': 'read',
                          'contents': 'read',
                          'issues': 'write',
                          'metadata': 'read',
                          'pull_requests': 'write',
                          'statuses': 'write'})

    def test_repositories(self):
        self.assertEqual({repo.full_name
                          for repo in self.installation.repositories},
                         {'gitmate-test-org/test'})
