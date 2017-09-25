"""
Contains a representation of GitHub users.
"""
from IGitt.GitLab import GL_INSTANCE_URL, GitLabMixin
from IGitt.Interfaces.User import User


class GitLabUser(GitLabMixin, User):
    """
    A GitLab user, e.g. sils :)
    """

    def __init__(self, id):
        self._url = f'/users/{id}'
        self._id = id

    @property
    def login(self):
        """
        Retrieves the login for the user.
        """
        return self.data['username']

    @property
    def id(self):
        """
        Gets a unique id for the user that never changes.
        """
        return self._id

    @property
    def url(self):
        """
        The web URL for the user.
        """
        return f'{GL_INSTANCE_URL}/{self.login}'
