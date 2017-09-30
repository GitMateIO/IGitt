import os
import pytest

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabNotification import GitLabNotification
from IGitt.Interfaces.Notification import Reason

from tests import IGittTestCase


class GitLabNotificationTest(IGittTestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.notification = GitLabNotification(self.token, '3789039')

    def test_id(self):
        self.assertEqual(self.notification.identifier, '3789039')

    def test_unsubscribe(self):
        self.assertIsNone(self.notification.unsubscribe())

    def test_mark_done(self):
        notification = GitLabNotification(self.token, '5574368')
        self.assertIsNone(notification.mark_done())
        self.assertEqual(notification.pending, False)
        # once marked as done, GitLab deletes the notification
        with pytest.raises(RuntimeError):
            notification.refresh()

    def test_reason(self):
        self.assertEqual(self.notification.reason, Reason.BUILD_FAILED)

    def test_subject_type(self):
        self.assertEqual(self.notification.subject_type, GitLabMergeRequest)

    def test_subject(self):
        self.assertIsInstance(self.notification.subject, GitLabMergeRequest)
        self.assertEqual(self.notification.subject.title, 'Sils/severalcommits')

    def test_repository(self):
        self.assertEqual(self.notification.repository.full_name,
                         'gitmate-test-user/test')

    def test_fetch_all(self):
        self.assertEqual(len(GitLabNotification.fetch_all(self.token)), 1)
