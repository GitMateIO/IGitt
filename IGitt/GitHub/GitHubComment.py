"""
Represents a comment on GitHub.
"""
from datetime import datetime

from IGitt.GitHub import delete, get
from IGitt.Interfaces.Comment import Comment


class GitHubComment(Comment):
    """
    Represents a comment on GitHub, mainly with a body and author - oh and it's
    deletable!
    """

    def __init__(self, oauth_token, repository, comment_id):
        """
        Creates a new GitHub comment from the given data.

        :param oauth_token: An OAuth token to use for authentication.
        :param repository: The full name of the repository.
        :param comment_id: The id of the comment.
        """
        self._token = oauth_token
        self._url = '/repos/'+repository+'/issues/comments/'+str(comment_id)

        self._data = get(self._token, self._url)

    @property
    def body(self):
        """
        Retrieves the content of the comment:

        >>> from os import environ
        >>> issue = GitHubComment(environ['GITHUB_TEST_TOKEN'],
        ...                      'gitmate-test-user/test', 172962077)
        >>> issue.body
        'test comment'

        :return: A string containing the body.
        """
        return self._data['body']

    @property
    def author(self):
        """
        Retrieves the username of the author:

        >>> from os import environ
        >>> issue = GitHubComment(environ['GITHUB_TEST_TOKEN'],
        ...                      'gitmate-test-user/test', 172962077)
        >>> issue.author
        'sils'

        :return: A string containing the authors username.
        """
        return self._data['user']['login']

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was created.

        >>> from os import environ
        >>> issue = GitHubComment(environ['GITHUB_TEST_TOKEN'],
        ...                      'gitmate-test-user/test', 172962077)
        >>> issue.created
        datetime.datetime(2016, 1, 19, 19, 37, 53)
        """
        return datetime.strptime(self._data['created_at'],
                                 "%Y-%m-%dT%H:%M:%SZ")

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was updated the last time.

        >>> from os import environ
        >>> issue = GitHubComment(environ['GITHUB_TEST_TOKEN'],
        ...                      'gitmate-test-user/test', 172962077)
        >>> issue.updated
        datetime.datetime(2016, 10, 9, 11, 36, 7)
        """
        return datetime.strptime(self._data['updated_at'],
                                 "%Y-%m-%dT%H:%M:%SZ")

    def delete(self):
        """
        Deletes the comment.
        """
        delete(self._token, self._url)
