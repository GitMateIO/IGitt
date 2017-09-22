import unittest
import os

import vcr
import requests_mock

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubOrganization import GitHubOrganization


my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class GitHubOrganizationTest(unittest.TestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.org = GitHubOrganization(self.token, 'gitmate-test-org')
        self.user = GitHubOrganization(self.token, 'gitmate-test-user')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_organization_billable_users.yaml')
    def test_billable_users(self):
        self.assertEqual(self.org.billable_users, 3) # sils, nkprince007, gitmate-test-user
        self.assertEqual(self.user.billable_users, 1) # gitmate-test-user

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_organization_admins.yaml')
    def test_admins(self):
        self.assertEqual(self.org.admins, {'sils', 'nkprince007'})
        self.assertEqual(self.user.admins, {'gitmate-test-user'})
