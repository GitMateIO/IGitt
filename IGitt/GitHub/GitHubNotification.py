"""
This contains the Notification implementation for GitHub.

Take note that GitHub Notifications are actually available via Threads API and
Notifications API is just a wrapper to fetching these threads.
"""
from typing import Union

from IGitt.GitHub import delete
from IGitt.GitHub import get
from IGitt.GitHub import patch
from IGitt.GitHub import GitHubMixin
from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.Interfaces.Notification import Notification
from IGitt.Interfaces.Notification import Reason


class GitHubNotification(GitHubMixin, Notification):
    """
    This class represents a Notification on GitHub.
    """

    def __init__(self, token: GitHubToken, identifier: Union[str, int]):
        """
        Creates a new GitHubNotification object with the given credentials.
        """
        self._token = token
        self._id = str(identifier)
        self._url = '/notifications/threads/' + self._id

    @property
    def identifier(self) -> str:
        """
        Returns the id of the notification thread from GitHub.
        """
        return self._id

    @property
    def reason(self) -> Reason:
        """
        Returns the reason for notification.
        """
        return {
            'assign': Reason.ASSIGNED,
            'author': Reason.AUTHORED,
            'comment': Reason.COMMENTED,
            'invitation': Reason.INVITED,
            'mention': Reason.MENTIONED,
            'manual': Reason.MANUAL,
            'state_change': Reason.STATE_CHANGED,
            'subscribed': Reason.SUBSCRIBED,
            'team_mention': Reason.MENTIONED
        }[self.data['reason']]

    @property
    def subject_type(self) -> type:
        """
        Returns the type of the subject the notification.
        """
        return {
            'Commit': GitHubCommit,
            'Issue': GitHubIssue,
            'PullRequest': GitHubMergeRequest
        }[self.data['subject']['type']]

    @property
    def subject(self) -> Union[GitHubCommit, GitHubIssue, GitHubMergeRequest]:
        """
        Returns the subject of the notification.

        :return: A GitHubCommit, GitHubIssue or GitHubMergeRequest object.
        """
        subject_data = self.data['subject']
        identifier = subject_data['url'].strip().split('/')[-1]
        return self.subject_type.from_data(subject_data, self._token,
                                           self.repository.full_name,
                                           identifier)

    @property
    def repository(self) -> GitHubRepository:
        """
        Returns the repository this notification is related to.
        """
        return GitHubRepository.from_data(self.data['repository'],
                                          self._token,
                                          self.data['repository']['full_name'])

    @property
    def pending(self) -> bool:
        """
        Returns True if the notification is pending/not read.
        """
        return self.data['unread'] or False

    def unsubscribe(self):
        """
        Unsubscribe from this subject.
        """
        delete(self._token, self._url + '/' + 'subscription')

    def mark_done(self):
        """
        Marks the notification as done/read.
        """
        patch(self._token, self._url, {})
        self.data.update({'unread': False})

    @staticmethod
    def fetch_all(token: GitHubToken):
        """
        Returns the list of notifications for the user bearing the token.
        """
        return [GitHubNotification.from_data(notif, token, notif['id'])
                for notif in get(token, '/notifications')]
