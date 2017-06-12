"""
This contains the Issue implementation for GitHub.
"""
from datetime import datetime

from IGitt.GitHub import get, patch, post
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.Interfaces.Comment import CommentType
from IGitt.Interfaces.Issue import Issue


class GitHubIssue(Issue):
    """
    This class represents an issue on GitHub.
    """

    def __init__(self, oauth_token: str, repository: str, issue_number: int):
        """
        Creates a new GitHubIssue with the given credentials.

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/repo_that_doesnt_exist', 1)
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
         ...
        RuntimeError: ({'message': 'Not Found', ...}, 404)

        :param oauth_token: The OAuth token.
        :param repository: The full name of the repository,
                           e.g. ``sils/something``.
        :param issue_number: The issue number.
        :raises RuntimeError: If something goes wrong (network, auth, ...)
        """
        self._token = oauth_token
        self._repository = repository
        self._url = '/repos/'+repository+'/issues/'+str(issue_number)
        self._data = get(self._token, self._url)

    @property
    def title(self):
        """
        Retrieves the title of the issue.

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.title
        'test issue'

        You can simply set it using the property setter:

        >>> issue.title = 'dont panic'
        >>> issue.title
        'dont panic'

        >>> issue.title = 'test issue'

        :return: The title of the issue - as string.
        """
        return self._data['title']

    @title.setter
    def title(self, new_title):
        """
        Sets the title of the issue.

        :param new_title: The new title.
        """
        self._data = patch(self._token, self._url, {'title': new_title})

    @property
    def url(self):
        """
        Returns the link/URL of the issue.
        """
        return 'https://github.com/{}/issues/{}'.format(self._repository,
                                                        self.number)

    @property
    def number(self) -> int:
        """
        Returns the issue "number" or id.

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.number
        1

        :return: The number of the issue.
        """
        return self._data['number']

    @property
    def assignee(self):
        """
        Retrieves the assignee of the issue:

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.assignee
        'gitmate-test-user'

        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 2)
        >>> issue.assignee  # Returns None, unassigned

        :return: A string containing the username or None.
        """
        return (self._data['assignee']['login'] if self._data['assignee'] else
                None)

    @property
    def description(self):
        r"""
        Retrieves the main description of the issue:

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.description
        'A nice description!\n'

        :return: A string containing the main description of the issue.
        """
        return self._data['body']

    def add_comment(self, body):
        """
        Adds a comment to the issue:

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 3)
        >>> comment = issue.add_comment("Doh!")

        You can use the comment right after:

        >>> comment.body
        'Doh!'
        >>> comment.delete()

        The comment will be created by the user authenticated via the oauth
        token.

        :param body: The body of the new comment to create.
        :return: The newly created comment.
        """
        result = post(self._token, self._url + '/comments', {'body': body})

        return GitHubComment(self._token, self._repository,
                             CommentType.ISSUE, result['id'])

    @property
    def comments(self):
        r"""
        Retrieves comments from the issue.

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 9)
        >>> comments = issue.comments

        Now we can e.g. access the last comment:

        >>> comments[-1].body
        'Do not comment here.\n'

        :return: A list of Comment objects.
        """
        return [GitHubComment(self._token, self._repository,
                              CommentType.ISSUE, result['id'])
                for result in get(self._token, self._url + '/comments')]

    @property
    def labels(self):
        """
        Retrieves all labels associated with this bug.

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.labels
        set()

        Use the property setter to set the labels:

        >>> issue.labels = {'a', 'b', 'c'}
        >>> sorted(issue.labels)
        ['a', 'b', 'c']

        Use the empty set intuitively to clear all labels:

        >>> issue.labels = set()

        :return: A list of label captions (str).
        """
        return set(label['name'] for label in self._data['labels'])

    @labels.setter
    def labels(self, value: {str}):
        """
        Sets the labels to the given set of labels.

        :param value: A set of label texts.
        """
        self._data = patch(self._token, self._url, {'labels': list(value)})

    @property
    def available_labels(self):
        """
        Retrieves a set of captions that are available for labelling bugs.

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> sorted(issue.available_labels)
        ['a', 'b', 'c']

        :return: A set of label captions (str).
        """
        return {label['name'] for label in get(
            self._token, '/repos/' + self._repository + '/labels')}

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the issue was created.

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.created
        datetime.datetime(2016, 1, 13, 7, 56, 23)
        """
        return datetime.strptime(self._data['created_at'],
                                 "%Y-%m-%dT%H:%M:%SZ")

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the issue was updated the last time.

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 9)
        >>> issue.updated
        datetime.datetime(2016, 10, 9, 11, 27, 11)
        """
        return datetime.strptime(self._data['updated_at'],
                                 "%Y-%m-%dT%H:%M:%SZ")

    def close(self):
        """
        Closes the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self._data = patch(self._token, self._url, {"state": "closed"})

    def reopen(self):
        """
        Reopens the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self._data = patch(self._token, self._url, {"state": "open"})

    def delete(self):
        """
        Should delete the issue, but GitHub doesn't allow it yet.

        Reference: https://github.com/isaacs/github/issues/253
        """
        raise NotImplementedError("GitHub doesn't allow deleting issues.")

    @property
    def state(self) -> str:
        """
        Get's the state of the issue.

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 10)
        >>> issue.state
        'open'

        So if we close it:

        >>> issue.close()
        >>> issue.state
        'closed'

        And reopen it:

        >>> issue.reopen()
        >>> issue.state
        'open'

        :return: Either 'open' or 'closed'.
        """
        return self._data['state']

    @staticmethod
    def create(token: str, repository: str,
               title: str, body: str=''):
        """
        Create a new issue with given title and body.

        >>> from os import environ
        >>> issue = GitHubIssue.create(environ['GITHUB_TEST_TOKEN'],
        ...                       'gitmate-test-user/test',
        ...                       'test issue title',
        ...                       'sample description')
        >>> issue.state
        'open'

        Let's delete the newly created one, because it's useless.

        >>> issue.delete()
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
         ...
        NotImplementedError

        Because GitHub is stupid, they don't allow deleting issues. So, let's
        atleast close this for now.

        >>> issue.close()

        :return: GitHubIssue object of the newly created issue.
        """

        post_url = '/repos/' + repository + '/issues'
        data = {
            "title": title,
            "body": body,
        }

        resp = post(token, post_url, data)
        issue_number = resp['number']

        return GitHubIssue(token, repository, issue_number)
