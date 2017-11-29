"""
This contains the Notification implementation for GitHub.

Take note that GitHub Notifications are actually available via Todos API.
"""
from functools import lru_cache
from typing import Union

from IGitt.GitLab import get
from IGitt.GitLab import post
from IGitt.GitLab import BASE_URL
from IGitt.GitLab import GitLabMixin
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab import GitLabPrivateToken
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.Interfaces.Notification import Notification
from IGitt.Interfaces.Notification import Reason


class GitLabNotification(GitLabMixin, Notification):
    """
    This class represents a Notification on GitLab.
    """
    def __init__(self,
                 token: Union[GitLabOAuthToken, GitLabPrivateToken],
                 identifier: Union[str, int]):
        """
        Creates a new GitLabNotification object with the given credentials.
        """
        self._token = token
        self._id = str(identifier)
        self._url = '/todos/' + self._id

    @property
    def identifier(self) -> str:
        """
        Returns the id of the notification thread from GitLab.
        """
        return self._id

    @property
    def reason(self) -> Reason:
        """
        Returns the reason for notification.
        """
        return {
            'assigned': Reason.ASSIGNED,
            'mentioned': Reason.MENTIONED,
            'directly_addressed': Reason.MENTIONED,
            'marked': Reason.MARKED,
            'build_failed': Reason.BUILD_FAILED,
            'approval_required': Reason.APPROVAL_REQUIRED
        }[self.data['action_name']]

    @property
    def subject_type(self) -> type:
        """
        Returns the type of the subject the notification.
        """
        return {
            'MergeRequest': GitLabMergeRequest,
            'Issue': GitLabIssue
        }[self.data['target_type']]

    @property
    def subject(self) -> Union[GitLabIssue, GitLabMergeRequest]:
        """
        Returns the subject of the notification.

        :return: A GitLabIssue or GitLabMergeRequest object.
        """
        subject_data = self.data['target']
        return self.subject_type.from_data(subject_data, self._token,
                                           self.repository.full_name,
                                           subject_data['iid'])

    @property
    def repository(self) -> GitLabRepository:
        """
        Returns the repository this notification is related to.
        """
        return GitLabRepository(self._token,
                                self.data['project']['path_with_namespace'])

    @property
    def pending(self) -> bool:
        """
        Returns True if the notification is pending/not read.
        """
        return self.data['state'] == 'pending'

    def unsubscribe(self):
        """
        Unsubscribe from this subject.
        """
        url = '{}/unsubscribe'.format(self.subject.url.replace(BASE_URL, ''))
        self.data = post(self._token, url, {})

    def mark_done(self):
        """
        Marks the notification as done/read.
        """
        self.data = post(self._token, self._url + '/mark_as_done', {})

    def _get_data(self):
        try:
            return [todo for todo in self._fetch_all(self._token)
                    if str(todo['id']) == self.identifier][0]
        except IndexError:
            # Couldn't find the matching notification
            raise RuntimeError({'error':'404 Not Found'}, 404)

    @staticmethod
    @lru_cache(None)
    def _fetch_all(token):
        return get(token, '/todos')

    @staticmethod
    def fetch_all(token: Union[GitLabPrivateToken, GitLabOAuthToken]):
        """
        Returns the list of notifications for the user bearing the token.
        """
        return [GitLabNotification.from_data(data, token, data['id'])
                for data in GitLabNotification._fetch_all(token)]
