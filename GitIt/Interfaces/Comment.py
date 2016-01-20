"""
This module contains the Comment class representing a comment on a pull
request, commit or issue.
"""


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

    def delete(self):
        """
        Deletes this comment at the hosting site.

        :raises RuntimeError: If the hosting service doesn't support deletion.
        """
        raise NotImplementedError
