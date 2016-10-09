"""
This module contains the Issue abstraction class which provides properties and
actions related to issues and bug reports.
"""
from datetime import datetime

from IGitt.Interfaces.Comment import Comment


class Issue:
    """
    Represents an issue on GitHub or GitLab or a bug report on bugzilla or so.
    """

    @property
    def number(self) -> int:
        """
        Returns the issue "number" or id.
        """
        raise NotImplementedError

    @property
    def title(self) -> str:
        """
        Retrieves the title of the issue.
        """
        raise NotImplementedError

    @title.setter
    def title(self, new_title):
        """
        Sets the title of the issue.

        :param new_title: The new title.
        """
        raise NotImplementedError

    @property
    def description(self) -> str:
        """
        Retrieves the main description of the issue.
        """
        raise NotImplementedError

    @property
    def assignee(self) -> str:
        """
        Retrieves the username of the assigned user or None.
        """
        raise NotImplementedError

    @assignee.setter
    def assignee(self, username: str):
        """
        Sets the assignee to the given user.

        :param username: A string containing the username of the user.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def labels(self) -> {str}:
        """
        Retrieves the set of labels the issue is currently tagged with.

        :return: The set of labels.
        """
        raise NotImplementedError

    @labels.setter
    def labels(self, value: {str}):
        """
        Tags the issue with the given labels. For examples see documentation
        of the labels read function.

        Labels are added and removed as necessary on remote.

        :param value: The new set of labels.
        """
        raise NotImplementedError

    @property
    def available_labels(self) -> {str}:
        """
        Compiles a set of labels that are available for labelling this issue.

        :return: A set of label captions.
        """
        raise NotImplementedError

    @property
    def comments(self) -> [Comment]:
        """
        Retrieves a list of comments which are on the issue excliding the description.

        :return: A list of Comment objects.
        """
        raise NotImplementedError

    def add_comment(self, body) -> Comment:
        """
        Adds a comment to the issue.

        :param body: The content of the comment.
        :return: The newly created comment.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was created.
        """
        raise NotImplementedError

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was updated the last time.
        """
        raise NotImplementedError
