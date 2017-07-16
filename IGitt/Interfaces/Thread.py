"""
Contains the Thread class.
"""


class Thread:
    """
    Represents an thread on GitHub or GitLab or a bug report on bugzilla or so.
    """

    @property
    def reason(self) -> str:
        """
        Returns the "reason" of notification.
        """
        raise NotImplementedError

    @property
    def unread(self) -> bool:
        """
        Returns a boolean representing whether the notification is read or not.
        """
        raise NotImplementedError

    def mark(self):
        """
        Marks the thread as read
        """
        raise NotImplementedError

    def unsubscribe(self):
        """
        Unsubscribe from the thread notifications
        """
        raise NotImplementedError
