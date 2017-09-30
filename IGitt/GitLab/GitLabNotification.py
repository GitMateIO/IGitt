"""
This contains the Notification implementation for GitHub.

Take note that GitHub Notifications are actually available via Todos API.
"""
from IGitt.GitLab import get
from IGitt.GitLab import post
from IGitt.GitLab import GitLabMixin
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab import GitLabPrivateToken
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.Interfaces.Notification import Notification
from IGitt.Interfaces.Notification import Reason
from IGitt.Interfaces.Notification import Subject


class GitLabNotificationManager(GitLabMixin):
    """
    The class that manages notifications/Todos from GitLab. Since GitLab
    doesn't provide a GET API for individual notifications, we manage them on
    our own.
    """
    def __init__(self, token: (GitLabOAuthToken, GitLabPrivateToken)):
        self._token = token

    def refresh(self):
        self._todos = [
            GitLabNotification.from_data(todo, self._token, todo['id'])
            for todo in get(self._token, '/todos')
        ]

    def list(self):
        if not getattr(self, '_todos', None):
            self.refresh()
        return self._todos

    def get(self, identifier: str):
        try:
            return list(filter(lambda todo: todo.identifier == identifier,
                               self.list()))[0]
        except IndexError:
            raise RuntimeError({'error':'404 Not Found'}, 404)

class GitLabNotification(GitLabMixin, Notification):
    """
    This class represents a Notification on GitLab.
    """
    def refresh(self):
        """
        Refresh the notification by fetching data again.
        """
        self._manager.refresh()

    @property
    def data(self):
        """
        Retrieves the data from the manager.
        """
        if not getattr(self, '_data', None):
            self._data = self._manager.get(self.identifier)._data
        return self._data

    @data.setter
    def data(self, value: dict):
        if not isinstance(value, dict):
            raise TypeError('%r is not of type %r' % (type(value), dict))
        self._data = value

    def __init__(self,
                 token: (GitLabOAuthToken, GitLabPrivateToken),
                 identifier: (str, int)):
        """
        Creates a new GitLabNotification object with the given credentials.
        """
        self._token = token
        self._id = str(identifier)
        self._url = '/todos/' + self._id
        self._manager = GitLabNotificationManager(self._token)

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
            'marked': Reason.MARKED,
            'build_failed': Reason.BUILD_FAILED,
            'approval_required': Reason.APPROVAL_REQUIRED
        }.get(self.data['action_name'])

    @property
    def subject_type(self) -> Subject:
        """
        Returns the type of the subject the notification.
        """
        return {
            'MergeRequest': Subject.MERGE_REQUEST,
            'Issue': Subject.ISSUE
        }.get(self.data['target_type'])

    @property
    def subject(self):
        """
        Returns the subject of the notification.

        :return: A GitLabIssue or GitLabMergeRequest object.
        """
        subject_data = self.data['target']
        subject = {
            Subject.MERGE_REQUEST: GitLabMergeRequest,
            Subject.ISSUE: GitLabIssue
        }.get(self.subject_type)
        return subject.from_data(subject_data, self._token,
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
        Unsubscribe from the this notification.
        """
        raise NotImplementedError('No subscriptions for Todos on GitLab')

    def mark_done(self):
        """
        Marks the notification as done/read.
        """
        self.data = post(self._token, self._url + '/mark_as_done', {})

    @staticmethod
    def fetch_all(token: (GitLabPrivateToken, GitLabOAuthToken)):
        """
        Returns the list of notifications for the user bearing the token.
        """
        return [GitLabNotification.from_data(notif, token, notif['id'])
                for notif in get(token, '/todos')]
