"""
Contains the git Hoster abstraction.
"""
from IGitt.Interfaces.Repository import Repository


class Hoster:
    """
    Abstracts a service like GitHub and allows e.g. to query for available
    repositories and stuff like that.
    """
    @property
    def master_repositories(self) -> {Repository}:
        """
        Retrieves the repositories the user has administrative access to.
        """
        raise NotImplementedError

    @property
    def owned_repositories(self) -> {Repository}:
        """
        Retrieves the full names of the owned repositories as strings.

        :return: A set of strings.
        """
        raise NotImplementedError

    @property
    def write_repositories(self) -> {Repository}:
        """
        Retrieves the full names of repositories this user can write to.

        :return: A set of strings.
        """
        raise NotImplementedError

    def get_repo(self, repository) -> Repository:
        """
        Return a repository object.
        """
        raise NotImplementedError
