"""
Contains a representation of GitHub users.
"""
from typing import Optional
from typing import Union

from IGitt.GitLab import GitLabMixin
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab import GitLabPrivateToken
from IGitt.Interfaces.User import User


class GitLabUser(GitLabMixin, User):
    """
    A GitLab user, e.g. sils :)
    """

    def __init__(self,
                 token: Union[GitLabPrivateToken, GitLabOAuthToken],
                 identifier: Optional[int]=None):
        """
        Creates a new user.

        :param token: The oauth token object
        :param identifier: Pass None if it's you! Otherwise the id, integer.
        """
        self._token = token
        if identifier:
            identifier = self._identifier_from_username(identifier)
            self._url = '/users/' + str(identifier)
        else:
            self._url = '/user'
        self._id = identifier

    @property
    def username(self) -> str:
        """
        Retrieves the login for the user.
        """
        return self.data['username']

    @property
    def identifier(self) -> int:
        """
        Gets a unique id for the user that never changes.
        """
        return self._id or self.data['id']

    def _identifier_from_username(self, username: str) -> int:
        """
        Returns identifier of the user with given username.
        """
        res = get(self._token, '/users', {'username': username})
        for item in res:
            if item['username'] == username:
                self.data = item
                return item['id']
        raise RuntimeError('User {} doesn\'t exist'.format(username))

    def installed_repositories(self, installation_id: int):
        """
        List repositories that are accessible to the authenticated user for an
        installation.

        GitLab doesn't support building installations yet.
        """
        raise NotImplementedError
