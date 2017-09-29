"""
Contains a representation of GitHub users.
"""
from IGitt.GitLab import GitLabMixin
from IGitt.Interfaces.User import User


class GitLabUser(GitLabMixin, User):
    """
    A GitLab user, e.g. sils :)
    """

    def __init__(self, token, identifier):
        """
        Creates a new user.

        :param token: The oauth token object
        :param identifier: Pass None if it's you! Otherwise the id, integer.
        """
        self._token = token
        self._url = '/users/' + str(identifier) if identifier else '/user'
        self._id = identifier

    @property
    def username(self):
        """
        Retrieves the login for the user.
        """
        return self.data['username']

    @property
    def identifier(self):
        """
        Gets a unique id for the user that never changes.
        """
        return self._id or self.data['id']
