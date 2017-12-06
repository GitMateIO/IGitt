"""
This module contains the Comment class representing a comment on a pull
request, commit or issue.
"""
from datetime import datetime
from enum import Enum

from IGitt.Interfaces import IGittObject
from IGitt.Interfaces.Repository import Repository
from IGitt.Interfaces.User import User


class CommentType(Enum):
    """
    An abstract class to differentiate types of comments.
    """
    ISSUE = 'issues'
    SNIPPET = 'snippets'
    MERGE_REQUEST = 'merge_requests'
    COMMIT = 'commits'
    REVIEW = 'review'


class Comment(IGittObject):
    """
    A comment, essentially represented by body and author.
    """

    @property
    def number(self) -> int:
        """
        Retrieves the id of the comment.
        """
        raise NotImplementedError

    @property
    def type(self):
        """
        Retrieves the type of the comment.
        """
        raise NotImplementedError

    @property
    def body(self) -> str:
        """
        Retrieves the body of the comment.
        """
        raise NotImplementedError

    @body.setter
    def body(self, value):
        """
        Edits the comment body at the hosting site to value.
        """
        raise NotImplementedError

    @property
    def author(self) -> User:
        """
        Retrieves the author of the comment wrapped in a User object.
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

    def delete(self):
        """
        Deletes this comment at the hosting site.

        :raises RuntimeError: If the hosting service doesn't support deletion.
        """
        raise NotImplementedError

    @property
    def repository(self) -> Repository:
        """
        Retrieves the repository in which the comment was posted.
        """
        raise NotImplementedError
