"""
This module contains the Issue abstraction class which provides properties and
actions related to issues and bug reports.
"""
from urllib.parse import quote_plus

from IGitt.GitLab import GL_INSTANCE_URL, GitLabMixin
from IGitt.GitLab import get
from IGitt.Interfaces.Organization import Organization


class GitLabOrganization(Organization, GitLabMixin):
    """
    Represents an organization on GitLab.
    """

    def __init__(self, token, name):
        """
        :param name: Name of the org.
        """
        self._token = token
        self._name = name
        self._url = '/groups/{name}'.format(name=quote_plus(name))

    @property
    def billable_users(self) -> int:
        """
        Number of paying/registered users on the organization.
        """
        return len(get(self._token, self._url + '/members'))


    @property
    def admins(self) -> set(str):
        """
        Returns the user handles of all admin users.
        """
        return {
            user['username']
            for user in get(self._token, self._url + '/members')
            if user['access_level'] >= 50
        }

    @property
    def name(self) -> str:
        """
        The name of the organization.
        """
        return self._name

    @property
    def url(self):
        """
        Returns the link/URL of the issue.
        """
        return GL_INSTANCE_URL + '/groups/{}'.format(self.name)
