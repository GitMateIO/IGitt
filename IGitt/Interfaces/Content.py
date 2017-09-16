"""
This module contains the Content class.
"""
from abc import ABCMeta
from abc import abstractmethod


class Content(metaclass=ABCMeta):
    """
    Represents content on GitHub or GitLab or a bug report on bugzilla or so.
    """

    @abstractmethod
    def get_content(self, ref: (str, None)=None):
        """
        Get content
        """

    @abstractmethod
    def delete(self, message: str, branch: (str, None)=None):
        """
        Delete content
        """

    @abstractmethod
    def update(self, message: str, content: str,
               branch: (str, None)=None):
        """
        Updates existing file in repository
        """
