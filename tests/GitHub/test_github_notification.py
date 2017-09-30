import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubNotification import GitHubNotification
from IGitt.Interfaces.Notification import Reason
from IGitt.Interfaces.Notification import Subject

from tests import IGittTestCase


class GitHubNotificationTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.notification = GitHubNotification(self.token, '262245073')

    def test_id(self):
        self.assertEqual(self.notification.identifier, '262245073')

    def test_unsubscribe(self):
        self.assertIsNone(self.notification.unsubscribe())

    def test_mark_done(self):
        self.assertIsNone(self.notification.mark_done())
        self.assertEqual(self.notification.pending, False)

    def test_reason(self):
        self.assertEqual(self.notification.reason, Reason.SUBSCRIBED)

    def test_subject_type(self):
        self.assertEqual(self.notification.subject_type, Subject.ISSUE)

    def test_subject(self):
        self.assertIsInstance(self.notification.subject, GitHubIssue)
        self.assertEqual(self.notification.subject.title, 'Hello')

    def test_repository(self):
        self.assertEqual(self.notification.repository.full_name,
                         'gitmate-test-user-2/issue')

    def test_fetch_all(self):
        self.assertEqual(GitHubNotification.fetch_all(self.token), [])
