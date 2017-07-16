"""
This contains the Thread implementation for GitHub.
"""
from IGitt.GitHub import GitHubMixin, GitHubToken, patch, delete
from IGitt.Interfaces.Thread import Thread


class GitHubThread(Thread, GitHubMixin):
    """
    This class represents a thread on GitHub
    """

    def __init__(self, token: GitHubToken, thread_id):
        self._token = token
        self._id = thread_id
        self._url = '/notifications/threads/' + self._id

    def unsubscribe(self):
        delete(self._token, self._url + '/' + 'subscription')

    def mark(self):
        self.data = patch(self._token, self._url, {})

    @property
    def reason(self):
        return self.data['reason']

    @property
    def unread(self):
        return self.data['unread']
