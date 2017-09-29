"""
Contains a representation of GitHub users.
"""
from IGitt.GitHub import GitHubMixin
from IGitt.Interfaces.User import User


class GitHubUser(GitHubMixin, User):
    """
    A GitHub user, e.g. sils :)
    """

    def __init__(self, token, username):
        self._token = token
        self._url = '/users/' + username
        self._username = username

    @property
    def username(self):
        """
        Retrieves the login for the user.
        """
        return self._username

    @property
    def identifier(self):
        """
        Gets a unique id for the user that never changes.
        """
        return self.data['id']
