"""
This module contains the Issue abstraction class which provides properties and
actions related to issues and bug reports.
"""
from datetime import datetime
from typing import Set
from typing import List

from IGitt.Interfaces import IGittObject
from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.Repository import Repository
from IGitt.Interfaces.User import User


class Issue(IGittObject):
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
    def repository(self) -> Repository:
        """
        Returns the repository this issue is linked with.
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

    @description.setter
    def description(self, new_description):
        """
        Sets the description of the issue.

        :param new_description: The new description.
        """
        raise NotImplementedError

    @property
    def author(self) -> User:
        """
        Retrieves the author of the comment wrapped in a User object.
        """
        raise NotImplementedError

    @property
    def assignees(self) -> Set[User]:
        """
        Retrieves a set of usernames of assignees.
        """
        raise NotImplementedError

    @assignees.setter
    def assignees(self, value: Set[User]):
        """
        Setter for ssignees.
        """
        raise NotImplementedError

    def assign(self, *usernames: List[User]):
        """
        Sets a given users as assignee.
        """
        raise NotImplementedError

    def unassign(self, *usernames: List[User]):
        """
        Unassigns given users from issue.
        """
        raise NotImplementedError

    @property
    def labels(self) -> Set[str]:
        """
        Retrieves the set of labels the issue is currently tagged with.

        :return: The set of labels.
        """
        raise NotImplementedError

    @labels.setter
    def labels(self, value: Set[str]):
        """
        Tags the issue with the given labels. For examples see documentation
        of the labels read function.

        Labels are added and removed as necessary on remote.

        :param value: The new set of labels.
        """
        raise NotImplementedError

    @property
    def available_labels(self) -> Set[str]:
        """
        Compiles a set of labels that are available for labelling this issue.

        :return: A set of label captions.
        """
        raise NotImplementedError

    @property
    def comments(self) -> List[Comment]:
        """
        Retrieves a list of comments which are on the issue excliding the
        description.

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

    def close(self):
        """
        Closes the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def reopen(self):
        """
        Reopens the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def delete(self):
        """
        Deletes the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def state(self) -> str:
        """
        Get's the state of the issue.

        :return: Either 'open' or 'closed'.
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

    @property
    def reactions(self) -> List[str]:
        """
        Retrieves the reactions / award emojis applied on the issue.
        """
        raise NotImplementedError

    @staticmethod
    def create(token, repository, title, body=''):
        """
        Create a new issue in repository.
        """
        raise NotImplementedError

    @property
    def mrs_closed_by(self) -> Set:
        """
        Returns the merge requests that close this issue.
        """
        raise NotImplementedError
