"""
This module contains the Comment class representing a comment on a pull
request, commit or issue.
"""
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty
from datetime import datetime
from enum import Enum

from IGitt.Interfaces.Repository import Repository


class CommentType(Enum):
    """
    An abstract class to differentiate types of comments.
    """
    ISSUE = 'issues'
    SNIPPET = 'snippets'
    MERGE_REQUEST = 'merge_requests'
    COMMIT = 'commits'


class Comment(metaclass=ABCMeta):
    """
    A comment, essentially represented by body and author.
    """

    @abstractproperty
    def number(self) -> int:
        """
        Retrieves the id of the comment.
        """

    @abstractproperty
    def type(self):
        """
        Retrieves the type of the comment.
        """

    @abstractproperty
    def body(self) -> str:
        """
        Retrieves the body of the comment.
        """

    @body.setter
    @abstractmethod
    def body(self, value):
        """
        Edits the comment body at the hosting site to value.
        """

    @abstractproperty
    def author(self) -> str:
        """
        Retrieves the username of the author of the comment.
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

    @abstractmethod
    def delete(self):
        """
        Deletes this comment at the hosting site.

        :raises RuntimeError: If the hosting service doesn't support deletion.
        """

    @abstractproperty
    def repository(self) -> Repository:
        """
        Retrieves the repository in which the comment was posted.
        """
