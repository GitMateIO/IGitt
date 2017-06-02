"""
Contains the Hoster implementation for GitLab.
"""

from IGitt.GitLab import get
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces.Hoster import Hoster


class GitLab(Hoster):
    """
    A high level interface to GitLab.
    """

    def __init__(self, oauth_token):
        """
        Creates a new GitLab Hoster object.

        :param oauth_token: An OAuth token to use for authentication.
        """
        self._token = oauth_token

    @property
    def owned_repositories(self):
        """
        Retrieves repositories owned by the authenticated user.

        >>> from os import environ
        >>> GitLab = GitLab(environ['GITLAB_TEST_TOKEN'])
        >>> GitLab.owned_repositories
        {'gitmate-test-user/test'}

        :return: A set of full repository names.
        """
        repo_list = get(self._token, '/projects', {'owned': True})
        return {repo['path_with_namespace'] for repo in repo_list}

    @property
    def write_repositories(self):
        """
        Retrieves the full names of repositories this user can write to.

        >>> from os import environ
        >>> GitLab = GitLab(environ['GITLAB_TEST_TOKEN'])
        >>> sorted(GitLab.write_repositories)
        ['gitmate-test-user/test', 'nkprince007/gitmate-test']

        :return: A set of strings.
        """
        repo_list = get(self._token, '/projects', {'membership': True})
        return {repo['path_with_namespace'] for repo in repo_list
                if repo['permissions']['project_access']['access_level'] >=
                AccessLevel.CAN_WRITE.value}

    def get_repo(self, repository):
        """
        Retrieve a given repository.
        """
        raise NotImplementedError
