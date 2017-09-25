"""
Contains a representation of GitHub users.
"""
from IGitt.GitHub import GitHubMixin, GH_INSTANCE_URL
from IGitt.Interfaces.User import User


class GitHubUser(GitHubMixin, User):
    """
    A GitHub user, e.g. sils :)
    """

    def __init__(self, username):
        self._url = f'/users/{username}'
        self._username = username

    @property
    def login(self):
        """
        Retrieves the login for the user.
        """
        return self._username

    @property
    def id(self):
        """
        Gets a unique id for the user that never changes.
        """
        return self.data['id']

    @property
    def url(self):
        """
        The web URL for the user.
        """
        return f'{GH_INSTANCE_URL}/{self.login}'
