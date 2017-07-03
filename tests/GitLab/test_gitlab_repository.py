import unittest
import os
import time
from datetime import datetime

import vcr

from IGitt.GitLab import GitLabOAuthToken, GitLabPrivateToken
from IGitt.GitLab.GitLabContent import GitLabContent
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.Interfaces.Repository import WebhookEvents
from IGitt import ElementAlreadyExistsError, ElementDoesntExistError

my_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path'],
                 filter_query_parameters=['access_token', 'private_token'],
                 filter_post_data_parameters=['access_token', 'private_token'])


class TestGitLabRepository(unittest.TestCase):

    def setUp(self):
        token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.repo = GitLabRepository(token,
                                     'gitmate-test-user/test')

        self.fork_token = GitLabPrivateToken(os.environ.get('GITLAB_COAFILE_BOT_TOKEN', ''))
        self.fork_repo = GitLabRepository(self.fork_token,
                                          'gitmate-test-user/test')

    def test_hoster(self):
        self.assertEqual(self.repo.hoster, 'gitlab')

    def test_full_name(self):
        self.assertEqual(self.repo.full_name, 'gitmate-test-user/test')

    def test_clone_url(self):
        self.assertEqual(self.repo.clone_url,
                         'https://{}@gitlab.com/gitmate-test-user/test.git'.format(
                             'oauth2:' + os.environ.get('GITLAB_TEST_TOKEN', ''))
                        )

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_get_labels.yaml')
    def test_get_labels(self):
        self.assertEqual(sorted(self.repo.get_labels()), ['a', 'b', 'c', 'dem'])

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_create_label.yaml')
    def test_labels(self):
        with self.assertRaises(ElementAlreadyExistsError):
            self.repo.create_label('a', '#000000')

        with self.assertRaises(ElementDoesntExistError):
            self.repo.delete_label('f')

        self.repo.create_label('bug', '#000000')
        self.assertEqual(sorted(self.repo.get_labels()),
                         ['a', 'b', 'bug', 'c', 'dem'])
        self.repo.delete_label('bug')
        self.assertEqual(sorted(self.repo.get_labels()), ['a', 'b', 'c', 'dem'])

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_get_issue.yaml')
    def test_get_issue(self):
        self.assertEqual(self.repo.get_issue(1).title, 'new title')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_get_mr.yaml')
    def test_get_mr(self):
        self.assertEqual(self.repo.get_mr(2).title, 'Sils/severalcommits')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_create_issue.yaml')
    def test_create_issue(self):
        self.assertEqual(self.repo.create_issue(
            'title', 'body').title, 'title')

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_hooks.yaml')
    def test_hooks(self):
        self.repo.register_hook('http://some.url/in/the/world', 'secret',
                                events={WebhookEvents.MERGE_REQUEST})
        self.assertIn('http://some.url/in/the/world', self.repo.hooks)
        self.repo.register_hook('http://some.url/in/the/world')
        self.repo.delete_hook('http://some.url/in/the/world')
        self.assertNotIn('http://some.url/in/the/world', self.repo.hooks)
        self.repo.register_hook('http://some.url/in/the/world')
        self.assertIn('http://some.url/in/the/world', self.repo.hooks)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_merge_requests.yaml')
    def test_merge_requests(self):
        self.assertEqual(len(self.repo.merge_requests), 4)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_issues.yaml')
    def test_issues(self):
        self.assertEqual(len(self.repo.issues), 13)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_fork.yaml')
    def test_create_fork(self):
        try:
            fork = self.fork_repo.create_fork(namespace='coafile')
        except RuntimeError:
            fork = GitLabRepository(self.fork_token, 'coafile/test')
            fork.delete()
            time.sleep(5)
            fork = self.fork_repo.create_fork(namespace='coafile')

        self.assertIsInstance(fork, GitLabRepository)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_delete.yaml')
    def test_delete_repo(self):
        try:
            fork = self.fork_repo.create_fork(namespace='coafile')
        except RuntimeError:
            fork = GitLabRepository(self.fork_token, 'coafile/test')
            fork.delete()
            time.sleep(5)
            fork = self.fork_repo.create_fork(namespace='coafile')

        self.assertIsNone(fork.delete())

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_create_mr.yaml')
    def test_create_mr(self):
        try:
            fork = self.fork_repo.create_fork(namespace='coafile')
        except RuntimeError:
            fork = GitLabRepository(self.fork_token, 'coafile/test')
            fork.delete()
            time.sleep(5) # Waiting for repo deletion
            fork = self.fork_repo.create_fork(namespace='coafile')

        fork.create_file(path='.coafile', message='hello', content='hello', branch='master')
        mr = fork.create_merge_request(title='coafile', head='master', base='master',
                                       target_project_id=self.repo.data['id'],
                                       target_project=self.repo.data['path_with_namespace'])

        self.assertIsInstance(mr, GitLabMergeRequest)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_create_mr_with_author.yaml')
    def test_create_mr_with_author(self):
        try:
            fork = self.fork_repo.create_fork(namespace='coafile')
        except RuntimeError:
            fork = GitLabRepository(self.fork_token, 'coafile/test')
            fork.delete()
            time.sleep(5)  # Waiting for repo deletion
            fork = self.fork_repo.create_fork(namespace='coafile')
        author = {
            'name' : 'coafile',
            'email' : 'coafilecoala@gmail.com'
        }
        self.assertIsInstance(fork.create_file(path='.coafile', message='hello',
                                               content='hello', branch='master', author=author),
                              GitLabContent)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_create_file.yaml')
    def test_create_file(self):
        try:
            fork = self.fork_repo.create_fork(namespace='coafile')
        except RuntimeError:
            fork = GitLabRepository(self.fork_token, 'coafile/test')
            fork.delete()
            time.sleep(5)  # Waiting for repo deletion
            fork = self.fork_repo.create_fork(namespace='coafile')

        self.assertIsInstance(fork.create_file(path='.coafile', message='hello',
                                               content='hello', branch='master'),
                              GitLabContent)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_search_issues.yaml')
    def test_search_issues(self):
        created_after = datetime(2017, 6, 18).date()
        created_before = datetime(2017, 7, 15).date()
        issues = list(self.repo.search_issues(created_after=created_after,
                                              created_before=created_before))
        self.assertEqual(len(issues), 2)

    @my_vcr.use_cassette('tests/GitLab/cassettes/gitlab_repo_search_merge_requests.yaml')
    def test_search_mrs(self):
        updated_after = datetime(2017, 6, 18).date()
        updated_before = datetime(2017, 7, 2).date()
        merge_requests = list(self.repo.search_mrs(updated_after=updated_after,
                                                   updated_before=updated_before))
        self.assertEqual(len(merge_requests), 3)
