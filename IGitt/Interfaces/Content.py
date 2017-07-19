"""
This module contains the Content class.
"""


class Content:
    """
    Represents content on GitHub or GitLab or a bug report on bugzilla or so.
    """

    def get_content(self, ref: (str, None)=None):
        """
        Get content
        """
        raise NotImplementedError

    def delete(self, message: str, branch: (str, None)=None):
        """
        Delete content
        """
        raise NotImplementedError

    def update(self, message: str, content: str,
               branch: (str, None)=None):
        """
        Updates existing file in repository
        """
        raise NotImplementedError
