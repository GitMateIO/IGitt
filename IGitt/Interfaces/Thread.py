"""
Contains the Thread class.
"""
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

class Thread(metaclass=ABCMeta):
    """
    Represents an thread on GitHub or GitLab or a bug report on bugzilla or so.
    """

    @abstractproperty
    def reason(self) -> str:
        """
        Returns the "reason" of notification.
        """

    @abstractproperty
    def unread(self) -> bool:
        """
        Returns a boolean representing whether the notification is read or not.
        """

    @abstractmethod
    def mark(self):
        """
        Marks the thread as read
        """

    @abstractmethod
    def unsubscribe(self):
        """
        Unsubscribe from the thread notifications
        """
