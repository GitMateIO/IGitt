"""
Contains a representation of GitHub users.
"""
from typing import Optional

from IGitt.GitHub import GitHubMixin
from IGitt.GitHub import GitHubToken
from IGitt.Interfaces.User import User


class GitHubUser(GitHubMixin, User):
    """
    A GitHub user, e.g. sils :)
    """
    def __init__(self, token: GitHubToken, username: Optional[str]=None):
        """
        Creates a GitHubUser with the given credentials.

        :param token:       The Oauth token.
        :param username:    The username of github user.
                            Takes None, if it's the associated user's token.
        """
        self._token = token
        self._url = '/users/' + username if username else '/user'
        self._username = username

    @property
    def username(self) -> str:
        """
        Retrieves the login for the user.
        """
        return self._username or self.data['login']

    @property
    def identifier(self) -> int:
        """
        Gets a unique id for the user that never changes.
        """
        return self.data['id']
