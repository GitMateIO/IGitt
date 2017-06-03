"""
Represents a comment (or note) on GitLab.
"""
from urllib.parse import quote_plus

from datetime import datetime
from IGitt.GitLab import delete
from IGitt.GitLab import get
from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.Comment import CommentType


class GitLabComment(Comment):
    """
    Represents a comment (or note as GitLab folks call it), with mainly a body
    and an author, which can ofcourse be deleted.
    """

    def __init__(self, oauth_token: str, repository: str, iid: int,
                 comment_type: CommentType, comment_id: int):
        """
        Creates a new GitLabComment with the given data.

        :param oauth_token: An OAuth token to be used.
        :param repository: The full namespace of the repository.
        :param iid: The unique identifier that links the holder of comment to
                    GitLab. i.e. which identifies the MR or issue or snippet
                    the comment links to.
        :param comment_type: The type of comment it links to, either one of
                             GitLabComment types.
        :param comment_id: The id of comment.
        """
        self._token = oauth_token
        self._repository = repository
        self._type = comment_type
        self._url = '/projects/{repo}/{c_type}/{iid}/notes/{c_id}'.format(
            repo=quote_plus(repository), c_type=self._type.value,
            iid=iid, c_id=comment_id)
        self._data = get(self._token, self._url)

    @property
    def type(self) -> CommentType:
        """
        Retrieves the type of comment it links to.
        """
        return self._type

    @property
    def author(self) -> str:
        """
        Retrieves the username of the comment author.

        >>> from os import environ
        >>> note = GitLabComment(environ['GITLAB_TEST_TOKEN'],
        ...                      'gitmate-test-user/test', 1,
        ...                      CommentType.ISSUE, 31500135)
        >>> note.author
        'gitmate-test-user'

        :return: A string containing the author's username.
        """
        return self._data['author']['username']

    @property
    def body(self) -> str:
        r"""
        Retrieves the content of the comment.

        >>> from os import environ
        >>> note = GitLabComment(environ['GITLAB_TEST_TOKEN'],
        ...                      'gitmate-test-user/test', 1,
        ...                      CommentType.ISSUE, 31500135)
        >>> note.body
        'Lemme comment on you.\r\n'

        :return: A string containing the body.
        """
        return self._data['body']

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was created.

        >>> from os import environ
        >>> note = GitLabComment(environ['GITLAB_TEST_TOKEN'],
        ...                      'gitmate-test-user/test', 1,
        ...                      CommentType.ISSUE, 31500135)
        >>> note.created
        datetime.datetime(2017, 6, 5, 5, 20, 28, 418000)
        """
        return datetime.strptime(self._data['created_at'],
                                 '%Y-%m-%dT%H:%M:%S.%fZ')

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was updated the last time.

        >>> from os import environ
        >>> note = GitLabComment(environ['GITLAB_TEST_TOKEN'],
        ...                      'gitmate-test-user/test', 1,
        ...                      CommentType.ISSUE, 31500135)
        >>> note.updated
        datetime.datetime(2017, 6, 5, 6, 5, 34, 491000)
        """
        return datetime.strptime(self._data['updated_at'],
                                 '%Y-%m-%dT%H:%M:%S.%fZ')

    def delete(self):
        """
        Deletes the comment.
        """
        delete(self._token, self._url)
