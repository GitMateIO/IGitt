"""
Holds the User class representing users on such a platform.
"""
from IGitt.Interfaces import IGittObject


class User(IGittObject):
    """
    Represents a user on GitHub/Lab. If you want to uniquely identify a user,
    use the `id` property as the id will never change while the username might.
    """

    @property
    def username(self) -> str:
        """
        The username of the user. Warning: this might change when the user
        renames himself!
        """
        raise NotImplementedError

    @property
    def identifier(self) -> int:
        """
        A unique ID used to identify the user. This is also given in oauth
        records.
        """
        raise NotImplementedError
