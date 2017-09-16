"""
This module contains the Issue abstraction class which provides properties and
actions related to issues and bug reports.
"""
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty
from abc import abstractstaticmethod
from datetime import datetime

from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.Repository import Repository


class Issue(metaclass=ABCMeta):
    """
    Represents an issue on GitHub or GitLab or a bug report on bugzilla or so.
    """

    @abstractproperty
    def number(self) -> int:
        """
        Returns the issue "number" or id.
        """

    @abstractproperty
    def repository(self) -> Repository:
        """
        Returns the repository this issue is linked with.
        """

    @abstractproperty
    def title(self) -> str:
        """
        Retrieves the title of the issue.
        """

    @abstractproperty
    def url(self) -> str:
        """
        Retrieves the url of the issue.
        """

    @title.setter
    @abstractmethod
    def title(self, new_title):
        """
        Sets the title of the issue.

        :param new_title: The new title.
        """

    @abstractproperty
    def description(self) -> str:
        """
        Retrieves the main description of the issue.
        """

    @abstractproperty
    def author(self) -> str:
        """
        Retrieves the username of the author of the comment.
        """

    @abstractproperty
    def assignees(self) -> {str}:
        """
        Retrieves a set of usernames of assignees.
        """

    @abstractmethod
    def assign(self, username: str):
        """
        Sets a given user as assignee.
        """

    @abstractmethod
    def unassign(self, username: str):
        """
        Unassigns given user from issue.
        """

    @abstractproperty
    def labels(self) -> {str}:
        """
        Retrieves the set of labels the issue is currently tagged with.

        :return: The set of labels.
        """

    @labels.setter
    @abstractmethod
    def labels(self, value: {str}):
        """
        Tags the issue with the given labels. For examples see documentation
        of the labels read function.

        Labels are added and removed as necessary on remote.

        :param value: The new set of labels.
        """

    @abstractproperty
    def available_labels(self) -> {str}:
        """
        Compiles a set of labels that are available for labelling this issue.

        :return: A set of label captions.
        """

    @abstractproperty
    def comments(self) -> [Comment]:
        """
        Retrieves a list of comments which are on the issue excliding the description.

        :return: A list of Comment objects.
        """

    @abstractmethod
    def add_comment(self, body) -> Comment:
        """
        Adds a comment to the issue.

        :param body: The content of the comment.
        :return: The newly created comment.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """

    @abstractmethod
    def close(self):
        """
        Closes the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """

    @abstractmethod
    def reopen(self):
        """
        Reopens the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """

    @abstractmethod
    def delete(self):
        """
        Deletes the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """

    @abstractproperty
    def state(self) -> str:
        """
        Get's the state of the issue.

        :return: Either 'open' or 'closed'.
        """

    @abstractproperty
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was created.
        """

    @abstractproperty
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was updated the last time.
        """

    @abstractstaticmethod
    def create(token, repository, title, body=''):
        """
        Create a new issue in repository.
        """
