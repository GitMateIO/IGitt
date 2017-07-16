import unittest
import os

import vcr

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubContent import GitHubContent
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.Interfaces.Repository import WebhookEvents
from IGitt import ElementAlreadyExistsError, ElementDoesntExistError

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token'],
                 filter_post_data_parameters=['access_token'])


class TestGitHubRepository(unittest.TestCase):

    def setUp(self):
        token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        fork_token = GitHubToken(os.environ.get('GITHUB_COAFILE_BOT_TOKEN', ''))
        self.repo = GitHubRepository(token,
                                     'gitmate-test-user/test')
        self.fork_repo = GitHubRepository(fork_token, 'gitmate-test-user/test')

    def test_hoster(self):
        self.assertEqual(self.repo.hoster, 'github')

    def test_full_name(self):
        self.assertEqual(self.repo.full_name, 'gitmate-test-user/test')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_clone_url.yaml')
    def test_clone_url(self):
        self.assertEqual(self.repo.clone_url,
                         'https://{}@github.com/gitmate-test-user/test.git'.format(
                             os.environ.get('GITHUB_TEST_TOKEN', ''))
                        )

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_get_labels.yaml')
    def test_get_labels(self):
        self.assertEqual(sorted(self.repo.get_labels()), ['a', 'b', 'c'])

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_create_label.yaml')
    def test_labels(self):
        with self.assertRaises(ElementAlreadyExistsError):
            self.repo.create_label('a', '000000')

        with self.assertRaises(ElementDoesntExistError):
            self.repo.delete_label('f')

        self.repo.create_label('bug', '000000')
        self.assertEqual(sorted(self.repo.get_labels()),
                         ['a', 'b', 'bug', 'c'])
        self.repo.delete_label('bug')
        self.assertEqual(sorted(self.repo.get_labels()), ['a', 'b', 'c'])

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_get_issue.yaml')
    def test_get_issue(self):
        self.assertEqual(self.repo.get_issue(1).title, 'test issue')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_get_mr.yaml')
    def test_get_mr(self):
        self.assertEqual(self.repo.get_mr(11).title, 'testpr closing/opening')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_issues.yaml')
    def test_issues(self):
        self.assertEqual(len(self.repo.issues), 81)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_merge_requests.yaml')
    def test_merge_requests(self):
        self.assertEqual(len(self.repo.merge_requests), 3)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_create_issue.yaml')
    def test_create_issue(self):
        self.assertEqual(self.repo.create_issue(
            'title', 'body').title, 'title')

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_hooks.yaml')
    def test_hooks(self):
        self.repo.register_hook('http://some.url/in/the/world', '...',
                                events={WebhookEvents.PUSH})
        self.assertIn('http://some.url/in/the/world', self.repo.hooks)
        self.repo.register_hook('http://some.url/in/the/world')
        self.repo.delete_hook('http://some.url/in/the/world')
        self.assertNotIn('http://some.url/in/the/world', self.repo.hooks)
        self.repo.register_hook('http://some.url/in/the/world')
        self.assertIn('http://some.url/in/the/world', self.repo.hooks)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_create_fork.yaml')
    def test_create_fork(self):
        self.assertIsInstance(self.fork_repo.create_fork(), GitHubRepository)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_delete.yaml')
    def test_repo_delete(self):
        fork = self.fork_repo.create_fork()
        self.assertIsNone(fork.delete())

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_create_mr.yaml')
    def test_create_mr(self):
        fork = self.fork_repo.create_fork()
        try:
            fork.create_file('.coafile', 'Hello', 'Hello', 'master')
        except RuntimeError:
            fork.delete()
            fork = self.fork_repo.create_fork()
            fork.create_file('.coafile', 'Hello', 'Hello', 'master')
        self.assertIsInstance(
            self.fork_repo.create_merge_request('add', head='coafile:master',
                                                base='master'), GitHubMergeRequest)

    @my_vcr.use_cassette('tests/GitHub/cassettes/github_repo_create_file.yaml')
    def test_create_file(self):
        fork = self.fork_repo.create_fork()
        try:
            file = fork.create_file('.coafile', 'Hello', 'Hello', 'master')
        except RuntimeError:
            fork.delete()
            fork = self.fork_repo.create_fork()
            file = fork.create_file('.coafile', 'Hello', 'Hello', 'master')

        self.assertIsInstance(file, GitHubContent)
