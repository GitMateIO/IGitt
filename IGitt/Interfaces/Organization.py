"""
This module contains the Issue abstraction class which provides properties and
actions related to issues and bug reports.
"""


class Organization:
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
    def owners(self) -> {str}:
        """
        Returns the user handles of all admin users, usually the owner role.
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """
        The name of the organization.
        """
        raise NotImplementedError

    @property
    def url(self) -> str:
        """
        Retrieves the url of the issue.
        """
        raise NotImplementedError
