"""
This module contains the Content class.
"""
from typing import Optional

from IGitt.Interfaces import IGittObject


class Content(IGittObject):
    """
    Represents content on GitHub or GitLab or a bug report on bugzilla or so.
    """

    def get_content(self, ref: Optional[str]=None):
        """
        Get content
        """
        raise NotImplementedError

    def delete(self, message: str, branch: Optional[str]=None):
        """
        Deletes content

        :param message: The commit message for the deletion commit.
        :param branch:  The branch to delete this content from. Defaults to
                        `master`.
        """
        raise NotImplementedError

    def update(self, message: str, content: str, branch: Optional[str]=None):
        """
        Updates existing file in repository
        """
        raise NotImplementedError
