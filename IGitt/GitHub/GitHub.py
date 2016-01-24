"""
Contains the Hoster implementation for GitHub.
"""

from IGitt.GitHub import query
from IGitt.Interfaces.Hoster import Hoster


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
    def owned_repositories(self):
        """
        Retrieves repositories owned by the authenticated user.

        >>> from os import environ
        >>> github = GitHub(environ['GITHUB_TEST_TOKEN'])
        >>> github.owned_repositories
        {'gitmate-test-user/test'}

        :return: A set of full repository names.
        """
        repo_list = query(self._token, '/user/repos')
        return {repo['full_name']
                for repo in repo_list if repo['permissions']['admin']}
