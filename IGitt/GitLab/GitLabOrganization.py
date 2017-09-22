"""
This module contains the Issue abstraction class which provides properties and
actions related to issues and bug reports.
"""
from functools import lru_cache
from urllib.parse import quote_plus

from IGitt.GitLab import GL_INSTANCE_URL, GitLabMixin
from IGitt.GitLab import get
from IGitt.Interfaces import AccessLevel
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
        self._is_user = None

    @lru_cache()
    def raw_members(self) -> list:
        """
        Gets all members including the ones of groups around subgroups as a
        list of dicts from the JSON responses.
        """
        members = list(get(self._token, self._url + '/members'))
        if '/' in self.name:
            members.extend(GitLabOrganization(
                self._token,
                self.name.rsplit('/', maxsplit=1)[0]).raw_members())

        return members

    @property
    def billable_users(self) -> int:
        """
        Number of paying/registered users on the organization.
        """
        try:
            # If the org is a user, this'll throw RuntimeError
            users = {user['username'] for user in get(self._token,
                                                      self._url + '/members')}

            for group in get(self._token, '/groups'):
                gname = group['full_path']
                if (gname in self.name or self.name in gname) \
                        and self.name != gname:
                    users |= {
                        user['username']
                        for user in get(
                            self._token,
                            '/groups/{name}/members'.format(
                                name=quote_plus(gname)
                            )
                        )
                    }

            return len(users)
        except RuntimeError:
            return 1

    @property
    def owners(self) -> {str}:
        """
        Returns the user handles of all admin users.
        """
        try:
            return {
                user['username']
                for user in self.raw_members()
                if user['access_level'] >= AccessLevel.OWNER.value
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
        return GL_INSTANCE_URL + '/{}'.format(self.name)
