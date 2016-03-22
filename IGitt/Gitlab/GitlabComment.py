"""
Represents a note(comment) on  Gitlab.
"""

from IGitt.Gitlab import get
from IGitt.Interfaces.Comment import Comment


class GitlabComment(Comment):
    """
    Represents a note(comment) on Gitlab, mainly with a body and author
    - as the Gitlab api does not support deleting, we also can not.
    """

    def __init__(self, private_token, projectID, issueID, note_id):
        """
        Creates a new Gitlab note from the given data.

        :param private_token: A private token to use for authentication.
        :param repository: The full name of the repository.
        :param comment_id: The id of the comment.
        """
        self._token = private_token
        self._url = 'projects/'+str(projectID) +\
            '/issues/'+str(issueID)+'/notes/'+str(note_id)

        self._data = get(self._token, self._url)

    @property
    def body(self):
        """
        Retrieves the content of the comment:

        >>> from os import environ
        >>> issue = GitlabComment(environ['GITLAB_TEST_TOKEN'],
        ...                       915800, 1274759, 3988991)
        >>> issue.body
        'test issue comment'

        :return: A string containing the body.
        """
        return self._data['body']

    @property
    def author(self):
        """
        Retrieves the username of the author:

        >>> from os import environ
        >>> issue = GitlabComment(environ['GITLAB_TEST_TOKEN'],
        ...                       915800, 1274759, 3988991)
        >>> issue.author
        'GitMateTest'

        :return: A string containing the authors username.
        """
        return self._data['author']['username']

    def delete(self):
        """
        Deletes the comment.
        """
        raise RuntimeError(
            'Deleting comments is not supported by the Gitlab api.')
