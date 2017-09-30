import os

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabNotification import GitLabNotification
from IGitt.Interfaces.Notification import Reason
from IGitt.Interfaces.Notification import Subject

from tests import IGittTestCase


class GitLabNotificationTest(IGittTestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.notification = GitLabNotification(self.token, '3789039')

    def test_id(self):
        self.assertEqual(self.notification.identifier, '3789039')

    def test_unsubscribe(self):
        pass

    def test_mark_done(self):
        notification = GitLabNotification(self.token, '5574368')
        self.assertIsNone(notification.mark_done())
        from pprint import pprint as print
        print(notification.data)
        self.assertEqual(notification.pending, False)

    def test_reason(self):
        self.assertEqual(self.notification.reason, Reason.BUILD_FAILED)

    def test_subject_type(self):
        self.assertEqual(self.notification.subject_type, Subject.MERGE_REQUEST)

    def test_subject(self):
        self.assertIsInstance(self.notification.subject, GitLabIssue)
        self.assertEqual(self.notification.subject.title, 'Sils/severalcommits')

    def test_repository(self):
        self.assertEqual(self.notification.repository.full_name,
                         'gitmate-test-user/test')

    def test_fetch_all(self):
        self.assertEqual(len(GitLabNotification.fetch_all(self.token)), 1)
