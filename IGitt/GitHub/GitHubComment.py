"""
Represents a comment on GitHub.
"""

from IGitt.GitHub import delete_request, query
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

        self._data = query(self._token, self._url)

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
        'sils1297'

        :return: A string containing the authors username.
        """
        return self._data['user']['login']

    def delete(self):
        """
        Deletes the comment.
        """
        delete_request(self._token, self._url)
