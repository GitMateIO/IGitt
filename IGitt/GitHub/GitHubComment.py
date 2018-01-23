"""
Represents a comment on GitHub.
"""
from datetime import datetime

from IGitt.GitHub import delete, patch, GitHubMixin, GitHubToken
from IGitt.Interfaces.Comment import Comment, CommentType
from IGitt.GitHub.GitHubUser import GitHubUser


class GitHubComment(GitHubMixin, Comment):
    """
    Represents a comment on GitHub, mainly with a body and author - oh and it's
    deletable!
    """

    def __init__(self,
                 token: GitHubToken,
                 repository,
                 comment_type,
                 comment_id):
        """
        Creates a new GitHub comment from the given data.

        :param token: A GitHubToken  object to use for authentication.
        :param repository: The full name of the repository.
        :param comment_type: The type of comment it represents.
        :param comment_id: The id of the comment or the sha of commit in the
                           case of commit comments.
        """
        self._token = token
        self._type = comment_type
        self._id = int(comment_id)
        self._repository = repository

        if comment_type in [CommentType.MERGE_REQUEST, CommentType.ISSUE]:
            fixture = '/issues/comments'
        elif comment_type == CommentType.COMMIT:
            fixture = '/comments'
        elif comment_type == CommentType.REVIEW:
            fixture = '/pulls/comments'
        else: # No such comment has been implemented on GitHub yet
            raise NotImplementedError

        self._url = '/repos/{repo}{fixture}/{comment_id}'.format(
            repo=repository, fixture=fixture, comment_id=comment_id)

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
        return self._type

    @property
    def body(self):
        r"""
        Retrieves the content of the comment:

        >>> from os import environ
        >>> issue = GitHubComment(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                      'gitmate-test-user/test', 172962077)
        >>> issue.body
        'test comment\n'

        :return: A string containing the body.
        """
        return self.data['body']

    @body.setter
    def body(self, value: str):
        """
        Sets comment body to value on GitHub.

        :param value: A string containing comment body.
        """
        payload = {'body': value}
        self.data = patch(self._token, self._url, payload)

    @property
    def author(self) -> GitHubUser:
        """
        Retrieves the author of the comment.

        >>> from os import environ
        >>> issue = GitHubComment(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                      'gitmate-test-user/test', 172962077)
        >>> issue.author.username
        'sils'

        :return: A GitHubUser object.
        """
        return GitHubUser.from_data(self.data['user'],
                                    self._token,
                                    self.data['user']['login'])

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was created.

        >>> from os import environ
        >>> issue = GitHubComment(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                      'gitmate-test-user/test', 172962077)
        >>> issue.created
        datetime.datetime(2016, 1, 19, 19, 37, 53)
        """
        return datetime.strptime(self.data['created_at'],
                                 '%Y-%m-%dT%H:%M:%SZ')

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was updated the last time.

        >>> from os import environ
        >>> issue = GitHubComment(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                      'gitmate-test-user/test', 172962077)
        >>> issue.updated
        datetime.datetime(2016, 10, 9, 11, 36, 7)
        """
        return datetime.strptime(self.data['updated_at'],
                                 '%Y-%m-%dT%H:%M:%SZ')

    def delete(self):
        """
        Deletes the comment.
        """
        delete(self._token, self._url)

    @property
    def repository(self):
        """
        Returns the GitHub repository this comment was posted in, as a
        GitHubRepository instance.
        """
        from IGitt.GitHub.GitHubRepository import GitHubRepository
        return GitHubRepository(self._token, self._repository)
