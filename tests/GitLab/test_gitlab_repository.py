import os
from datetime import datetime

from IGitt.GitLab import GitLabOAuthToken, GitLabPrivateToken
from IGitt.GitLab.GitLabContent import GitLabContent
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.Interfaces.Repository import WebhookEvents
from IGitt import ElementAlreadyExistsError, ElementDoesntExistError

from tests import IGittTestCase


class GitLabRepositoryTest(IGittTestCase):

    def setUp(self):
        token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.repo = GitLabRepository(token,
                                     'gitmate-test-user/test')

        self.fork_token = GitLabPrivateToken(os.environ.get('GITLAB_COAFILE_BOT_TOKEN', ''))
        self.fork_repo = GitLabRepository(self.fork_token,
                                          'gitmate-test-user/test')

    def test_top_level_org(self):
        self.assertEqual(self.repo.top_level_org.name, 'gitmate-test-user')

    def test_hoster(self):
        self.assertEqual(self.repo.hoster, 'gitlab')

    def test_full_name(self):
        self.assertEqual(self.repo.full_name, 'gitmate-test-user/test')

    def test_clone_url(self):
        self.assertEqual(self.repo.clone_url,
                         'https://{}@gitlab.com/gitmate-test-user/test.git'.format(
                             'oauth2:' + os.environ.get('GITLAB_TEST_TOKEN', ''))
                        )

    def test_get_labels(self):
        self.assertEqual(sorted(self.repo.get_labels()), ['a', 'b', 'c', 'dem'])

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

    def test_get_issue(self):
        self.assertEqual(self.repo.get_issue(1).title, 'new title')

    def test_get_mr(self):
        self.assertEqual(self.repo.get_mr(2).title, 'Sils/severalcommits')

    def test_create_issue(self):
        self.assertEqual(self.repo.create_issue(
            'title', 'body').title, 'title')

    def test_hooks(self):
        self.repo.register_hook('http://some.url/in/the/world', 'secret',
                                events={WebhookEvents.MERGE_REQUEST})
        self.assertIn('http://some.url/in/the/world', self.repo.hooks)
        self.repo.register_hook('http://some.url/in/the/world')
        self.repo.delete_hook('http://some.url/in/the/world')
        self.assertNotIn('http://some.url/in/the/world', self.repo.hooks)
        self.repo.register_hook('http://some.url/in/the/world')
        self.assertIn('http://some.url/in/the/world', self.repo.hooks)

    def test_merge_requests(self):
        self.assertEqual(len(self.repo.merge_requests), 31)

    def test_issues(self):
        self.assertEqual(len(self.repo.issues), 14)

    def test_create_fork(self):
        try:
            fork = self.fork_repo.create_fork(namespace='coafile')
        except RuntimeError:
            fork = GitLabRepository(self.fork_token, 'coafile/test')
            fork.delete()
            fork = self.fork_repo.create_fork(namespace='coafile')

        self.assertIsInstance(fork, GitLabRepository)

    def test_delete_repo(self):
        try:
            fork = self.fork_repo.create_fork(namespace='coafile')
        except RuntimeError:
            fork = GitLabRepository(self.fork_token, 'coafile/test')
            fork.delete()
            fork = self.fork_repo.create_fork(namespace='coafile')

        self.assertIsNone(fork.delete())

    def test_create_mr(self):
        try:
            fork = self.fork_repo.create_fork(namespace='coafile')
        except RuntimeError:
            fork = GitLabRepository(self.fork_token, 'coafile/test')
            fork.delete()
            fork = self.fork_repo.create_fork(namespace='coafile')

        fork.create_file(path='.coafile', message='hello', content='hello', branch='master')
        mr = fork.create_merge_request(title='coafile', head='master', base='master',
                                       target_project_id=self.repo.data['id'],
                                       target_project=self.repo.data['path_with_namespace'])

        self.assertIsInstance(mr, GitLabMergeRequest)

    def test_create_mr_with_author(self):
        try:
            fork = self.fork_repo.create_fork(namespace='coafile')
        except RuntimeError:
            fork = GitLabRepository(self.fork_token, 'coafile/test')
            fork.delete()
            fork = self.fork_repo.create_fork(namespace='coafile')
        author = {
            'name' : 'coafile',
            'email' : 'coafilecoala@gmail.com'
        }
        self.assertIsInstance(fork.create_file(path='.coafile', message='hello',
                                               content='hello', branch='master', author=author),
                              GitLabContent)

    def test_create_file(self):
        try:
            fork = self.fork_repo.create_fork(namespace='coafile')
        except RuntimeError:
            fork = GitLabRepository(self.fork_token, 'coafile/test')
            fork.delete()
            fork = self.fork_repo.create_fork(namespace='coafile')

        self.assertIsInstance(fork.create_file(path='.coafile', message='hello',
                                               content='hello', branch='master'),
                              GitLabContent)

    def test_search_issues(self):
        created_after = datetime(2017, 6, 18).date()
        created_before = datetime(2017, 7, 15).date()
        issues = list(self.repo.search_issues(created_after=created_after,
                                              created_before=created_before))
        self.assertEqual(len(issues), 2)

    def test_search_mrs(self):
        updated_after = datetime(2017, 6, 18).date()
        updated_before = datetime(2017, 7, 2).date()
        merge_requests = list(self.repo.search_mrs(updated_after=updated_after,
                                                   updated_before=updated_before))
        self.assertEqual(len(merge_requests), 2)
