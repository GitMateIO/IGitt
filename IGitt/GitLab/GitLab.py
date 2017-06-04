"""
Contains the Hoster implementation for GitLab.
"""

from IGitt.GitLab import get
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces.Hoster import Hoster
from IGitt.GitLab.GitLabRepository import GitLabRepository


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
        >>> sorted(map(lambda x: x.full_name, GitLab.owned_repositories)
        {'gitmate-test-user/test'}

        :return: A set of GitLabRepository objects.
        """
        repo_list = get(self._token, '/projects', {'owned': True})
        return {GitLabRepository(self._token, repo['path_with_namespace'])
                for repo in repo_list}

    @property
    def write_repositories(self):
        """
        Retrieves the full names of repositories this user can write to.

        >>> from os import environ
        >>> GitLab = GitLab(environ['GITLAB_TEST_TOKEN'])
        >>> sorted(map(lambda x: x.full_name, GitLab.write_repositories))
        ['gitmate-test-user/test', 'nkprince007/gitmate-test']

        :return: A set of GitLabRepository objects.
        """
        repo_list = get(self._token, '/projects', {'membership': True})
        return {GitLabRepository(self._token, repo['path_with_namespace'])
                for repo in repo_list
                if repo['permissions']['project_access']['access_level'] >=
                AccessLevel.CAN_WRITE.value}

    def get_repo(self, repository) -> GitLabRepository:
        """
        Retrieve a given repository.

        >>> from os import environ
        >>> source = GitLab(environ['GITLAB_TEST_TOKEN'])
        >>> repo = source.get_repo('gitmate-test-user/test')
        >>> isinstance(repo, GitLabRepository)
        True

        :return: A repository object.
        """
        return GitLabRepository(self._token, repository)
