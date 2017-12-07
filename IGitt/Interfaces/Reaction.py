"""
Holds the Reaction class representing reactions on issues, comments and merge
requests.
"""
from IGitt.Interfaces import IGittObject
from IGitt.Interfaces.User import User


class Reaction(IGittObject):
    """
    Represents a reaction / award emoji on GitHub and GitLab.
    """

    @property
    def name(self) -> str:
        """
        Returns the name of the reaction.
        """
        raise NotImplementedError

    @property
    def user(self) -> User:
        """
        Returns the user who reacted with this.
        """
        raise NotImplementedError
