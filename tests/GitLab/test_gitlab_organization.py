import os

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabOrganization import GitLabOrganization

from tests import IGittTestCase


class GitLabOrganizationTest(IGittTestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))

        self.org = GitLabOrganization(self.token, 'gitmate-test-org')
        self.suborg = GitLabOrganization(self.token,
                                         'gitmate-test-org/subgroup')
        self.user = GitLabOrganization(self.token, 'gitmate-test-user')

    def test_billable_users(self):
        # All users from all sub orgs plus the one from main org
        self.assertEqual(self.org.billable_users, 5)
        # Users from this sub org plus main org
        self.assertEqual(self.suborg.billable_users, 4)
        self.assertEqual(self.user.billable_users, 1)

    def test_admins(self):
        self.assertEqual({o.username for o in self.suborg.owners},
                         {'sils', 'nkprince007'})
        self.assertEqual({o.username for o in self.org.owners},
                         {'sils', 'nkprince007'})
        self.assertEqual({m.username for m in self.org.masters},
                         {'sils', 'nkprince007', 'gitmate-test-user'})
        self.assertEqual({o.username for o in self.user.owners},
                         {'gitmate-test-user'})

    def test_organization(self):
        self.assertEqual(self.org.url,
                         'https://gitlab.com/api/v4/groups/gitmate-test-org')
        self.assertEqual(self.suborg.url,
                         'https://gitlab.com/api/v4/groups/gitmate-test-org%2Fsubgroup')
        self.assertEqual(self.user.url,
                         'https://gitlab.com/api/v4/groups/gitmate-test-user')
