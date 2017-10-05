"""
This module contains the GitHubInstallation class which provides
properties and actions related to GitHub App installations.
"""
from functools import lru_cache
from typing import List
from typing import Set

from IGitt.GitHub import get
from IGitt.GitHub import GitHubMixin
from IGitt.GitHub import GitHubInstallationToken
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.Interfaces.Installation import Installation


class GitHubInstallation(GitHubMixin, Installation):
    """
    Represents a GitHub App installation.
    """
    def __init__(self, token: GitHubInstallationToken, installation_id: int):
        """
        Creates a GitHubInstallation object with given credentials.
        """
        self._id = installation_id
        # jwt token is used to retrieve all properties
        self._token = token.jwt
        # installation token is used only for the api
        self._api_token = token
        self._url = '/app/installations/{}'.format(self._id)

    @property
    def identifier(self) -> int:
        """
        Returns the identifier of the installation.
        """
        return self._id

    @property
    def app_id(self) -> int:
        """
        The application which was installed.
        """
        return self.data['app_id']

    @property
    def webhooks(self) -> List[str]:
        """
        Returns the list of webhooks registered by installing the application.
        """
        return self.data['events']

    @property
    def permissions(self):
        """
        The permissions granted to this installation.
        """
        return self.data['permissions']

    @property
    @lru_cache(None)
    def repositories(self) -> Set[GitHubRepository]:
        """
        Returns the set of repositories this installation has access to.
        """
        data = get(self._api_token, '/installation/repositories')
        return {GitHubRepository.from_data(repo,
                                           self._api_token,
                                           repo['id'])
                for repo in data['repositories']}
