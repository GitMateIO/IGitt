"""
Contains the Hoster implementation for GitHub.
"""

from IGitt.GitHub import get
from IGitt.Interfaces.Hoster import Hoster
from IGitt.GitHub.GitHubRepository import GitHubRepository


class GitHub(Hoster):
    """
    A high level interface to GitHub.
    """

    def __init__(self, oauth_token):
        """
        Creates a new GitHub Hoster object.

        :param oauth_token: An OAuth token to use for authentication.
        """
        self._token = oauth_token

    @property
    def master_repositories(self):
        """
        Retrieves repositories the user has admin access to.
        """
        repo_list = get(self._token, '/user/repos')
        return {GitHubRepository(self._token, repo['full_name'])
                for repo in repo_list if repo['permissions']['admin']}

    @property
    def owned_repositories(self):
        """
        Retrieves repositories owned by the authenticated user.

        >>> from os import environ
        >>> github = GitHub(environ['GITHUB_TEST_TOKEN'])
        >>> sorted(map(lambda x: x.full_name, github.owned_repositories))
        ['gitmate-test-user/test']

        :return: A set of full repository names.
        """
        repo_list = get(self._token, '/user/repos', {'affiliation': 'owner'})
        return {GitHubRepository(self._token, repo['full_name'])
                for repo in repo_list}

    @property
    def write_repositories(self):
        """
        Retrieves the full names of repositories this user can write to.

        >>> from os import environ
        >>> github = GitHub(environ['GITHUB_TEST_TOKEN'])
        >>> sorted(map(lambda x: x.full_name, github.write_repositories))
        ['gitmate-test-user/test', 'sils/gitmate-test']

        :return: A set of strings.
        """
        repo_list = get(self._token, '/user/repos')
        return {GitHubRepository(self._token, repo['full_name'])
                for repo in repo_list if repo['permissions']['push']}

    def get_repo(self, repository) -> GitHubRepository:
        """
        Retrieve a given repository.

        >>> from os import environ
        >>> github = GitHub(environ['GITHUB_TEST_TOKEN'])
        >>> repo = github.get_repo('gitmate-test-user/test')
        >>> isinstance(repo, GitHubRepository)
        True

        :return: A repository object.
        """
        return GitHubRepository(self._token, repository)
