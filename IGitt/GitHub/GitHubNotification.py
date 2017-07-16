"""
This contains the Notification implementation for GitHub.
"""
from IGitt.GitHub import GitHubMixin, GitHubToken, get
from IGitt.GitHub.GitHubThread import GitHubThread
from IGitt.Interfaces.Notification import Notification


class GitHubNotification(Notification, GitHubMixin):
    """
    This class represents a Notification on GitHub
    """

    def __init__(self, token: GitHubToken):
        self._token = token
        self._url = '/notifications'

    def get_threads(self):
        return [GitHubThread(self._token, result['id'])
                for result in get(self._token, self._url)]
