"""
Contains the Notification base class.
"""
from abc import ABCMeta
from abc import abstractmethod
from IGitt.Interfaces import Thread


class Notification(metaclass=ABCMeta):
    """
    Represents a notification on GitHub or GitLab
    """

    @abstractmethod
    def get_threads(self) -> [Thread]:
        """
        Returns list of Threads
        """
