"""
Contains the Hoster implementation for GitLab.
"""

import logging

from IGitt.GitLab import get
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces.Hoster import Hoster
from IGitt.GitLab.GitLabRepository import GitLabRepository

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


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
    def master_repositories(self):
        """
        Retrieves repositories the user has admin access to.
        """
        repo_list = get(self._token, '/projects', {'membership': True})
        repos = []
        for repo in repo_list:
            perms = repo['permissions']
            project_access = perms['project_access'] or {}
            group_access = perms['group_access'] or {}
            access_level = max(project_access.get('access_level', 0),
                               group_access.get('access_level', 0))
            if access_level >= AccessLevel.ADMIN.value:
                repos.append(repo)
        return {GitLabRepository(self._token, repo['path_with_namespace'])
                for repo in repos}

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
        repos = []
        for repo in repo_list:
            perms = repo['permissions']
            project_access = perms['project_access'] or {}
            group_access = perms['group_access'] or {}
            access_level = max(project_access.get('access_level', 0),
                               group_access.get('access_level', 0))
            if access_level >= AccessLevel.CAN_WRITE.value:
                repos.append(repo)
        return {GitLabRepository(self._token, repo['path_with_namespace'])
                for repo in repos}

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
