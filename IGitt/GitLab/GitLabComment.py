"""
Represents a comment (or note) on GitLab.
"""
from typing import Union
from urllib.parse import quote_plus

from datetime import datetime
from IGitt.GitLab import delete, put, GitLabMixin
from IGitt.GitLab import GitLabOAuthToken, GitLabPrivateToken
from IGitt.GitLab.GitLabUser import GitLabUser
from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.Comment import CommentType


class GitLabComment(GitLabMixin, Comment):
    """
    Represents a comment (or note as GitLab folks call it), with mainly a body
    and an author, which can ofcourse be deleted.
    """

    def __init__(self, token: Union[GitLabOAuthToken, GitLabPrivateToken],
                 repository: str, iid: str, comment_type: CommentType,
                 comment_id: int):
        """
        Creates a new GitLabComment with the given data.

        :param token: A Token object to be used for authentication.
        :param repository: The full namespace of the repository.
        :param iid: The unique identifier that links the holder of comment to
                    GitLab. i.e. which identifies the MR (number) or
                    issue (number) or snippet (number) or commit (sha) the
                    comment links to.
        :param comment_type: The type of comment it links to, either one of
                             GitLabComment types.
        :param comment_id: The id of comment.
        """
        self._token = token
        self._repository = repository
        self._type = comment_type
        self._id = comment_id
        self._iid = str(iid)
        self._url = '/projects/{repo}/{c_type}/{iid}/notes/{c_id}'.format(
            repo=quote_plus(repository), c_type=self._type.value,
            iid=iid, c_id=comment_id)
        if comment_type == CommentType.REVIEW:
            raise NotImplementedError

    @property
    def iid(self) -> str:
        """
        Retrieves the internal identifier of the linked resource
        (issue/merge request/commit).
        """
        return self._iid

    @property
    def number(self) -> int:
        """
        Retrieves the id of the comment.
        """
        return self._id

    @property
    def type(self) -> CommentType:
        """
        Retrieves the type of comment it links to.
        """
        return self._type

    @property
    def author(self) -> GitLabUser:
        """
        Retrieves the author of the comment.

        >>> from os import environ
        >>> note = GitLabComment(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                      'gitmate-test-user/test', 1,
        ...                      CommentType.ISSUE, 31500135)
        >>> note.author.username
        'gitmate-test-user'

        :return: A GitLabUser object.
        """
        return GitLabUser.from_data(self.data['author'],
                                    self._token,
                                    self.data['author']['id'])

    @property
    def body(self) -> str:
        r"""
        Retrieves the content of the comment.

        >>> from os import environ
        >>> note = GitLabComment(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                      'gitmate-test-user/test', 1,
        ...                      CommentType.ISSUE, 31500135)
        >>> note.body
        'Lemme comment on you.\r\n'

        :return: A string containing the body.
        """
        return self.data['body']

    @body.setter
    def body(self, value: str):
        """
        Edits the body of the comment on GitLab.

        :param value: A string containing comment body.
        """
        payload = {'body': value}
        self.data = put(self._token, self._url, payload)

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was created.

        >>> from os import environ
        >>> note = GitLabComment(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                      'gitmate-test-user/test', 1,
        ...                      CommentType.ISSUE, 31500135)
        >>> note.created
        datetime.datetime(2017, 6, 5, 5, 20, 28, 418000)
        """
        return datetime.strptime(self.data['created_at'],
                                 '%Y-%m-%dT%H:%M:%S.%fZ')

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was updated the last time.

        >>> from os import environ
        >>> note = GitLabComment(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                      'gitmate-test-user/test', 1,
        ...                      CommentType.ISSUE, 31500135)
        >>> note.updated
        datetime.datetime(2017, 6, 5, 6, 5, 34, 491000)
        """
        return datetime.strptime(self.data['updated_at'],
                                 '%Y-%m-%dT%H:%M:%S.%fZ')

    def delete(self):
        """
        Deletes the comment.
        """
        delete(self._token, self._url)

    @property
    def repository(self):
        """
        Returns the GitLab repository this comment was posted in, as a
        GitLabRepository instance.
        """
        from IGitt.GitLab.GitLabRepository import GitLabRepository
        return GitLabRepository(self._token, self._repository)
