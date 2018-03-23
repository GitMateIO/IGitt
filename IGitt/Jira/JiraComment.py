"""
Represents the comment resource from JIRA.
"""
from datetime import datetime
from typing import Union

from IGitt.Interfaces import delete
from IGitt.Interfaces import put
from IGitt.Interfaces import BasicAuthorizationToken
from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.Comment import CommentType
from IGitt.Interfaces.User import User
from IGitt.Jira import JiraMixin
from IGitt.Jira import JiraOAuth1Token


class JiraComment(JiraMixin, Comment):
    """
    Represents a comment on JIRA, mainly with a body and author - oh and it's
    deletable!
    """

    def __init__(self,
                 token: Union[BasicAuthorizationToken, JiraOAuth1Token],
                 issue_id: Union[int, str],
                 comment_id: int):
        """
        Instantiates a new JiraComment instance from the given data.

        :param token:
            The token to be used for authentication.
        :param issue_id:
            The unique identifier or key for the issue on JIRA.
        :param comment_id:
            The unique identifier of the comment on JIRA.
        """
        self._token = token
        self._id = comment_id
        self._issue = issue_id
        self._url = '/issue/{}/comment/{}'.format(self._issue, self._id)

    @property
    def number(self) -> int:
        """
        Retrieves the id of the comment.
        """
        return self._id

    @property
    def type(self) -> CommentType:
        """
        Retrieves the type of the comment it links to.
        """
        return CommentType.ISSUE

    @property
    def body(self):
        """
        Retrieves the content of the comment:

        :return: A string containing the body.
        """
        return self.data['body']

    @body.setter
    def body(self, new_body: str):
        """
        Modifies the comment body to ``new_body``.

        :param new_body: A string containing comment body.
        """
        payload = {'body': new_body}
        self.data = put(self._token, self.url, payload)

    @property
    def author(self) -> User:
        """
        Retrieves the author of the comment.

        :return: A User object.
        """
        raise NotImplementedError

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was created.

        :return:    A datetime.datetime object representing the time of
                    creation of the comment.
        """
        return datetime.strptime(self.data['created'],
                                 '%Y-%m-%dT%H:%M:%S.%f%z')

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was updated the last time.

        :return:    A datetime.datetime object representing the time of the
                    last update of the comment.
        """
        return datetime.strptime(self.data['updated'],
                                 '%Y-%m-%dT%H:%M:%S.%f%z')

    def delete(self):
        """
        Deletes the comment.
        """
        delete(self._token, self.url)

    @property
    def repository(self):
        """
        Returns the JIRA project this comment was posted in, as a
        JiraRepository instance.
        """
        raise NotImplementedError
