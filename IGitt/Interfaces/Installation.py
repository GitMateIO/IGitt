"""
This module contains the Installation abstraction class which provides
properties and actions related to integration installations on supported
providers.
"""
from typing import Set
from typing import List

from IGitt.Interfaces import IGittObject
from IGitt.Interfaces.Repository import Repository


class Installation(IGittObject):
    """
    Represents an application Installation on supported providers.
    """

    @property
    def identifier(self) -> int:
        """
        Returns the identifier of the installation.
        """
        raise NotImplementedError

    @property
    def app_id(self) -> int:
        """
        The application which was installed.
        """
        raise NotImplementedError

    @property
    def webhooks(self) -> List[str]:
        """
        Returns the list of webhooks registered by installing the application.
        """
        raise NotImplementedError

    @property
    def permissions(self):
        """
        The permissions granted to this installation.
        """
        raise NotImplementedError

    @property
    def repositories(self) -> Set[Repository]:
        """
        Returns the set of repositories this installation has access to.
        """
        raise NotImplementedError
