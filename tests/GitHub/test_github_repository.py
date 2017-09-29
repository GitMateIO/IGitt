from datetime import datetime
import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubContent import GitHubContent
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.Interfaces.Repository import WebhookEvents
from IGitt import ElementAlreadyExistsError, ElementDoesntExistError

from tests import IGittTestCase


class GitHubRepositoryTest(IGittTestCase):

    def setUp(self):
        token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        fork_token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN_2', ''))
        self.repo = GitHubRepository(token,
                                     'gitmate-test-user/test')
        self.fork_repo = GitHubRepository(fork_token, 'gitmate-test-user/test')

    def test_top_level_org(self):
        self.assertEqual(self.repo.top_level_org.name, 'gitmate-test-user')

    def test_hoster(self):
        self.assertEqual(self.repo.hoster, 'github')

    def test_full_name(self):
        self.assertEqual(self.repo.full_name, 'gitmate-test-user/test')

    def test_clone_url(self):
        self.assertEqual(self.repo.clone_url,
                         'https://{}@github.com/gitmate-test-user/test.git'.format(
                             os.environ.get('GITHUB_TEST_TOKEN', ''))
                        )

    def test_get_labels(self):
        self.assertEqual(sorted(self.repo.get_labels()), ['a', 'b', 'c'])

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

    def test_get_issue(self):
        self.assertEqual(self.repo.get_issue(1).title, 'test issue')

    def test_get_mr(self):
        self.assertEqual(self.repo.get_mr(11).title, 'testpr closing/opening')

    def test_issues(self):
        self.assertEqual(len(self.repo.issues), 87)

    def test_merge_requests(self):
        self.assertEqual(len(self.repo.merge_requests), 13)

    def test_create_issue(self):
        self.assertEqual(self.repo.create_issue(
            'title', 'body').title, 'title')

    def test_hooks(self):
        self.repo.register_hook('http://some.url/in/the/world', '...',
                                events={WebhookEvents.PUSH})
        self.assertIn('http://some.url/in/the/world', self.repo.hooks)
        # won't register again
        self.repo.register_hook('http://some.url/in/the/world')
        self.repo.delete_hook('http://some.url/in/the/world')
        self.assertNotIn('http://some.url/in/the/world', self.repo.hooks)
        # events not specified, register all
        self.repo.register_hook('http://some.url/in/the/world')
        self.assertIn('http://some.url/in/the/world', self.repo.hooks)
        self.repo.delete_hook('http://some.url/in/the/world')

    def test_create_fork(self):
        self.assertIsInstance(self.fork_repo.create_fork(), GitHubRepository)

    def test_repo_delete(self):
        fork = self.fork_repo.create_fork()
        self.assertIsNone(fork.delete())

    def test_create_mr(self):
        fork = self.fork_repo.create_fork()
        try:
            fork.create_file('.coafile', 'Hello', 'Hello', 'master')
        except RuntimeError:
            fork.delete()
            fork = self.fork_repo.create_fork()
            fork.create_file('.coafile', 'Hello', 'Hello', 'master')
        self.assertIsInstance(
            self.fork_repo.create_merge_request('add', head='gitmate-test-user-2:master',
                                                base='master'), GitHubMergeRequest)

    def test_create_file(self):
        fork = self.fork_repo.create_fork()
        try:
            file = fork.create_file('.coafile', 'Hello', 'Hello', 'master')
        except RuntimeError:
            fork.delete()
            fork = self.fork_repo.create_fork()
            file = fork.create_file('.coafile', 'Hello', 'Hello', 'master')

        self.assertIsInstance(file, GitHubContent)

    def test_search_issues(self):
        date = datetime(2017, 6, 17).date()
        issues = [issue for issue in self.repo.search_issues(created_before=date)]
        self.assertEqual(len(issues), 75)
        issues = [issue for issue in self.repo.search_issues(created_after=date)]
        self.assertEqual(len(issues), 10)
        with self.assertRaises(RuntimeError):
            next(self.repo.search_issues(created_before=date, created_after=date))

    def test_search_mrs(self):
        date = datetime(2016, 1, 25).date()
        mrs = [mr for mr in self.repo.search_mrs(created_before=date)]
        self.assertEqual(len(mrs), 2)
        mrs = [mr for mr in self.repo.search_mrs(created_after=date)]
        self.assertEqual(len(mrs), 11)
        date = datetime(2017, 6, 18).date()
        mrs = [mr for mr in self.repo.search_mrs(updated_after=date)]
        self.assertEqual(len(mrs), 11)
        mrs = [mr for mr in self.repo.search_mrs(updated_before=date)]
        self.assertEqual(len(mrs), 2)
