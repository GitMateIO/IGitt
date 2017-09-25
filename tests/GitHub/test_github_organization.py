import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubOrganization import GitHubOrganization

from tests import IGittTestCase


class GitHubOrganizationTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.org = GitHubOrganization(self.token, 'gitmate-test-org')
        self.user = GitHubOrganization(self.token, 'gitmate-test-user')

    def test_billable_users(self):
        # sils, nkprince007, gitmate-test-user
        self.assertEqual(self.org.billable_users, 3)
        self.assertEqual(self.user.billable_users, 1) # gitmate-test-user

    def test_owners(self):
        self.assertEqual({o.username for o in self.org.owners},
                         {'nkprince007', 'sils'})
        self.assertEqual({m.username for m in self.org.masters},
                         {'nkprince007', 'sils'})
        self.assertEqual({o.username for o in self.user.owners},
                         {'gitmate-test-user'})
        self.assertEqual({m.username for m in self.user.masters},
                         {'gitmate-test-user'})

    def test_organization(self):
        self.assertEqual(self.org.url,
                         'https://github.com/gitmate-test-org')
        self.assertEqual(self.user.url,
                         'https://github.com/gitmate-test-user')
