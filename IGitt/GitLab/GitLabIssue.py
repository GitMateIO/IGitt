"""
This contains the Issue implementation for GitLab.
"""
from datetime import datetime
from urllib.parse import quote_plus

from IGitt.GitLab import delete
from IGitt.GitLab import get
from IGitt.GitLab import put
from IGitt.GitLab import post
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.Interfaces.Comment import CommentType
from IGitt.Interfaces.Issue import Issue


class GitLabIssue(Issue):
    """
    This class represents an issue on GitLab.
    """

    def __init__(self, oauth_token: str, repository: str, issue_iid: int):
        """
        Creates a new GitLabIssue with the given credentials.

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/repo_that_doesnt_exist', 1)
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        RuntimeError: ({'message': 'Not Found', ...}, 404)

        :param oauth_token: The OAuth token.
        :param repository: The full name of the repository.
                           e.g. ``sils/baritone``.
        :param issue_iid: The issue internal identification number.
        :raises RuntimeError: If something goes wrong (network, auth, ...)
        """
        self._token = oauth_token
        self._repository = repository
        self._url = '/projects/{repo}/issues/{issue_iid}'.format(
            repo=quote_plus(repository), issue_iid=issue_iid)
        self._data = get(self._token, self._url)

    @property
    def title(self) -> str:
        """
        Retrieves the title of the issue.

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.title
        'Take it serious, son!'

        You can simply set it using the property setter:

        >>> issue.title = 'dont panic'
        >>> issue.title
        'dont panic'

        >>> issue.title = 'Take it serious, son!'

        :return: The title of the issue - as string.
        """
        return self._data['title']

    @title.setter
    def title(self, new_title):
        """
        Sets the title of the issue.

        :param new_title: The new title.
        """
        self._data = put(self._token, self._url, {'title': new_title})

    @property
    def url(self):
        """
        Returns the link/URL of the issue.
        """
        return 'https://gitlab.com/{}/issues/{}'.format(self._repository,
                                                        self.number)

    @property
    def number(self) -> int:
        """
        Returns the issue "number" or id.

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.number
        1

        :return: The number of the issue.
        """
        return self._data['iid']

    @property
    def assignee(self):
        """
        Retrieves the assignee of the issue:

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.assignee
        'gitmate-test-user'

        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 2)
        >>> issue.assignee # Returns None, unassigned

        :return: A string containing the username or None.
        """
        # GitLab uses some stupid EE conformance to create a single element
        # array of assignee.
        return (self._data['assignees'][0]['username']
                if self._data['assignees'] else None)

    @property
    def description(self) -> str:
        r"""
        Retrieves the main description of the issue.

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.description
        'I am a serious issue. Fix me soon, dude.'

        :return: A string containing the main description of the issue.
        """
        return self._data['description']

    def add_comment(self, body):
        """
        Adds a comment to the issue.

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
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
        result = post(self._token, self._url + '/notes', {'body': body})

        return GitLabComment(self._token, self._repository, self.number,
                             CommentType.ISSUE, result['id'])

    @property
    def comments(self) -> [GitLabComment]:
        r"""
        Retrieves comments from the issue.

        As of now, the list of comments is not sorted. Related issue on GitLab
        CE here - https://gitlab.com/gitlab-org/gitlab-ce/issues/32057

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 3)
        >>> comments = issue.comments
        >>> for comment in comments:
        ...     print(comment.body)
        Stop staring at me.
        Go, get your work done.

        :return: A list of Comment objects.
        """
        return [GitLabComment(self._token, self._repository, self.number,
                              CommentType.ISSUE, result['id'])
                for result in get(self._token, self._url + '/notes')]

    @property
    def labels(self) -> {str}:
        """
        Retrieves all labels associated with this bug.

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
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
        return set(self._data['labels'])

    @labels.setter
    def labels(self, value: {str}):
        """
        Sets the value of labels to the given set of labels.

        :param value: A set of label texts.
        """
        self._data = put(self._token, self._url,
                         {'labels': ','.join(map(str, value))})

    @property
    def available_labels(self) -> {str}:
        """
        Retrieves a set of captions that are available for labelling bugs.

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> sorted(issue.available_labels)
        ['a', 'b', 'c']

        :return: A set of label captions (str).
        """
        return {label['name'] for label in get(
            self._token, '/projects/' +
            quote_plus(self._repository) + '/labels')}

    @property
    def created(self)->datetime:
        """
        Retrieves a timestamp on when the issue was created.

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 4)
        >>> issue.created
        datetime.datetime(2017, 6, 5, 9, 45, 20, 678000)
        """
        return datetime.strptime(self._data['created_at'],
                                 '%Y-%m-%dT%H:%M:%S.%fZ')

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the issue was updated the last time.

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 4)
        >>> issue.updated
        datetime.datetime(2017, 6, 5, 9, 45, 56, 115000)
        """
        return datetime.strptime(self._data['updated_at'],
                                 '%Y-%m-%dT%H:%M:%S.%fZ')

    def close(self):
        """
        Closes the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self._data = put(self._token, self._url, {'state_event': 'close'})

    def reopen(self):
        """
        Reopens the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self._data = put(self._token, self._url, {'state_event': 'reopen'})

    def delete(self):
        """
        Deletes the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        delete(self._token, self._url)

    @property
    def state(self):
        """
        Get's the state of the issue.

        >>> from os import environ
        >>> issue = GitLabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> issue.state
        'reopened'

        So if we close it:

        >>> issue.close()
        >>> issue.state
        'closed'

        And reopen it:

        >>> issue.reopen()
        >>> issue.state
        'reopened'

        :return: Either 'opened', 'reopened' or 'closed'.
        """
        return self._data['state']

    @staticmethod
    def create(token: str, repository: str, title: str, body: str=''):
        """
        Create a new issue with given title and body.

        >>> from os import environ
        >>> issue = GitLabIssue.create(environ['GITLAB_TEST_TOKEN'],
        ...                            'gitmate-test-user/test',
        ...                            'test issue title',
        ...                            'sample description')
        >>> issue.state
        'opened'

        Delete the issue to avoid filling the test repo with issues.

        >>> issue.delete()

        :return: GitLabIssue object of the newly created issue.
        """
        url = '/projects/{repo}/issues'.format(repo=quote_plus(repository))
        issue = post(token, url, {'title': title, 'description': body})

        return GitLabIssue(token, repository, issue['iid'])
