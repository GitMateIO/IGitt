"""
This module contains the Issue abstraction class which provides properties and
actions related to issues and bug reports.
"""
from urllib.parse import quote_plus

from IGitt.GitHub import GH_INSTANCE_URL, GitHubMixin
from IGitt.GitHub import get
from IGitt.Interfaces.Organization import Organization


class GitHubOrganization(Organization, GitHubMixin):
    """
    Represents an organization on GitLab.
    """

    def __init__(self, token, name):
        """
        :param name: Name of the org.
        """
        self._token = token
        self._name = name
        self._url = '/orgs/{name}'.format(name=quote_plus(name))

    @property
    def billable_users(self) -> int:
        """
        Number of paying/registered users on the organization.
        """
        try:
            return len(get(self._token, self._url + '/members'))
        except RuntimeError:
            return 1

    @property
    def owners(self) -> {str}:
        """
        Returns the user handles of all admin users.
        """
        try:
            return {
                user['login']
                for user in get(
                    self._token, self._url + '/members',
                    params={'role': 'admin'}
                )
            }
        except RuntimeError:
            return {self.name}

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
        return GH_INSTANCE_URL + '/{}'.format(self.name)
