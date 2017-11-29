"""
This module contains the Issue abstraction class which provides properties and
actions related to issues and bug reports.
"""
from functools import lru_cache
from typing import Set
from urllib.parse import quote_plus

from IGitt.GitLab import GL_INSTANCE_URL
from IGitt.GitLab import GitLabMixin
from IGitt.GitLab import get
from IGitt.GitLab.GitLabUser import GitLabUser
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces.Organization import Organization


class GitLabOrganization(GitLabMixin, Organization):
    """
    Represents an organization on GitLab.
    """
    @property
    def web_url(self):
        return '{}/{}'.format(GL_INSTANCE_URL, self.name)

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

    def _members(self, access_level):
        try:
            return {
                GitLabUser.from_data(user, self._token, user['id'])
                for user in self.raw_members()
                if user['access_level'] >= access_level
            }
        except RuntimeError:
            return {GitLabUser.from_data({'username': self.name},
                                         self._token, identifier=None)}

    @property
    def owners(self) -> Set[GitLabUser]:
        """
        Returns the user handles of all owner users.
        """
        return self._members(AccessLevel.OWNER.value)

    @property
    def masters(self) -> Set[GitLabUser]:
        """
        Returns the user handles of all master users.
        """
        return self._members(AccessLevel.ADMIN.value)

    @property
    def name(self) -> str:
        """
        The name of the organization.
        """
        return self._name
