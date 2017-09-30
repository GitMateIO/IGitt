"""
Contains the Notification base class.
"""
from enum import Enum
from typing import Union

from IGitt.Interfaces import IGittObject
from IGitt.Interfaces import Token
from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces.Repository import Repository


class Reason(Enum):
    """
    The enum representing the reason/action of a notification.
    """
    ASSIGNED = 'assigned'
    MENTIONED = 'mentioned'
    BUILD_FAILED = 'build_failed'
    MARKED = 'marked'
    APPROVAL_REQUIRED = 'approval_required'
    AUTHORED = 'authored'
    COMMENTED = 'commented'
    INVITED = 'invited'
    MANUAL = 'manual'
    STATE_CHANGED = 'state_changed'
    SUBSCRIBED = 'subscribed'


class Notification(IGittObject):
    """
    Represents a notification/todo on GitHub or GitLab.
    """
    @staticmethod
    def fetch_all(token: Token):
        """
        Returns the list of notifications for the user bearing the token.
        """
        raise NotImplementedError

    @property
    def reason(self) -> Reason:
        """
        Returns the reason for notification.
        """
        raise NotImplementedError

    @property
    def subject_type(self) -> type:
        """
        Returns the type of the subject of the notification.
        """
        raise NotImplementedError

    @property
    def subject(self) -> Union[Commit, Issue, MergeRequest]:
        """
        Returns the subject of notification.
        """
        raise NotImplementedError

    @property
    def pending(self) -> bool:
        """
        Returns True if the notification is pending/not read.
        """
        raise NotImplementedError

    @property
    def repository(self) -> Repository:
        """
        Returns the repository this notification is related to.
        """
        raise NotImplementedError

    @property
    def identifier(self) -> str:
        """
        Returns the id of the notification.
        """
        raise NotImplementedError

    def mark_done(self):
        """
        Marks the notification as done/read.
        """
        raise NotImplementedError

    def unsubscribe(self):
        """
        Unsubscribe from this subject.
        """
        raise NotImplementedError
