"""
Contains the Notification base class.
"""

from IGitt.Interfaces import Thread


class Notification:
    """
    Represents a notification on GitHub or GitLab
    """
    def get_threads(self) -> [Thread]:
        """
        Returns list of Threads
        """
        raise NotImplementedError
