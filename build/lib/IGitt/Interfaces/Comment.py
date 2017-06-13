"""
This module contains the Comment class representing a comment on a pull
request, commit or issue.
"""
from datetime import datetime


class Comment:
    """
    A comment, essentially represented by body and author.
    """

    @property
    def body(self) -> str:
        """
        Retrieves the body of the comment.
        """
        raise NotImplementedError

    @property
    def author(self) -> str:
        """
        Retrieves the username of the author of the comment.
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
