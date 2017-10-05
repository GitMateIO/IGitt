"""
This module contains the Issue abstraction class which provides properties and
actions related to issues and bug reports.
"""
from typing import Set

from IGitt.Interfaces import IGittObject
from IGitt.Interfaces.User import User


class Organization(IGittObject):
    """
    Represents an organization on GitHub or GitLab.
    """

    @property
    def billable_users(self) -> int:
        """
        Number of paying/registered users on the organization.
        """
        raise NotImplementedError

    @property
    def owners(self) -> Set[User]:
        """
        Returns the user handles of all admin users, usually the owner role.
        """
        raise NotImplementedError

    @property
    def masters(self) -> Set[User]:
        """
        Returns the user handles of all users able to manage members, usually
        the master role (sometimes no such role exists, then same as owners).
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """
        The name of the organization.
        """
        raise NotImplementedError
