"""
Here you go: GitHub organizations can be used in IGitt.
"""
from functools import lru_cache
from typing import Set
from urllib.parse import quote_plus

from IGitt.GitHub import GH_INSTANCE_URL
from IGitt.GitHub import GitHubMixin
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.Interfaces import get
from IGitt.Interfaces.Organization import Organization
from IGitt.Interfaces.Repository import Repository


class GitHubOrganization(GitHubMixin, Organization):
    """
    Represents an organization on GitHub.
    """

    @property
    def web_url(self):
        return '{}/{}'.format(GH_INSTANCE_URL, self.name)

    def __init__(self, token, name):
        """
        :param name: Name of the org.
        """
        self._token = token
        self._name = name
        self._url = '/orgs/{name}'.format(name=quote_plus(name))

    @property
    def description(self) -> str:
        """
        Returns the description of this organization.
        """
        return self.data['description']

    @property
    def billable_users(self) -> int:
        """
        Number of paying/registered users on the organization.
        """
        try:
            return len(get(self._token, self.url + '/members'))
        except RuntimeError:
            return 1

    @property
    def owners(self) -> Set[GitHubUser]:
        """
        Returns the user handles of all admin users.
        """
        try:
            return {
                GitHubUser.from_data(user, self._token, user['login'])
                for user in get(
                    self._token, self.url + '/members',
                    params={'role': 'admin'}
                )
            }
        except RuntimeError:
            return {GitHubUser(self._token, self.name)}

    @property
    def masters(self) -> Set[GitHubUser]:
        """
        Gets all owners (because there's no masters role on GitHub).
        """
        return self.owners

    @property
    def name(self) -> str:
        """
        The name of the organization.
        """
        return self._name

    @property
    def suborgs(self) -> Set[Organization]:
        """
        Returns the sub-organizations within this repository.
        """
        return set()

    @property
    @lru_cache(None)
    def repositories(self) -> Set[Repository]:
        """
        Returns the list of repositories contained in this organization.
        """
        from IGitt.GitHub.GitHubRepository import GitHubRepository

        return {GitHubRepository.from_data(repo, self._token, repo['id'])
                for repo in get(self._token, self.url + '/repos')}
