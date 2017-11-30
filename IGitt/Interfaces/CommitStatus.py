"""
This module contains the CommitStatus class as well as the actual Status class.
"""

from enum import Enum


class Status(Enum):
    """
    The actual status of a commit.
    """

    SUCCESS = 1  # The commit was verified.
    PENDING = 2  # The verification is ongoing.
    FAILED = 3  # Something's wrong with the commit.
    ERROR = 4  # Something went wrong and the commit could not be verified.
    CANCELED = 5  # The build was canceled
    RUNNING = 6  # The build is still in progress
    MANUAL = 7  # The build can be triggered manually
    CREATED = 8 # The build job is created
    SKIPPED = 9 # The build job was skipped

class CommitStatus:
    """
    The commit status including all metadata.
    """

    def __init__(self, status: Status, description: str='', context: str='',
                 url: str='') -> None:
        """
        Creates a new commit status.

        >>> status = CommitStatus(Status.FAILED, "Theres a problem!",
        ...                       "review/gitmate/manual", "gitmate.io")
        >>> str(status.status)
        'Status.FAILED'
        >>> status.description
        'Theres a problem!'
        >>> status.context
        'review/gitmate/manual'
        >>> status.url
        'gitmate.io'

        :param status: The actual status of the commit.
        :param description: A description text, should be short!
        :param context: A context, like ``review/gitmate/manual``.
        :param url: A URL that is usually available to the user to get more
        details about the status.
        """
        self.status = status
        self.description = description
        self.context = context
        self.url = url
