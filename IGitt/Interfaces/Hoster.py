"""
Contains the git Hoster abstraction.
"""
from abc import ABCMeta
from abc import abstractproperty
from abc import abstractmethod

from IGitt.Interfaces.Repository import Repository


class Hoster(metaclass=ABCMeta):
    """
    Abstracts a service like GitHub and allows e.g. to query for available
    repositories and stuff like that.
    """

    @abstractproperty
    def master_repositories(self) -> {Repository}:
        """
        Retrieves the repositories the user has administrative access to.
        """

    @abstractproperty
    def owned_repositories(self) -> {Repository}:
        """
        Retrieves the full names of the owned repositories as strings.

        :return: A set of strings.
        """

    @abstractproperty
    def write_repositories(self) -> {Repository}:
        """
        Retrieves the full names of repositories this user can write to.

        :return: A set of strings.
        """

    @abstractmethod
    def get_repo(self, repository) -> Repository:
        """
        Return a repository object.
        """
