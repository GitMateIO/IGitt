"""
This contains the Issue implementation for GitHub.
"""
from datetime import datetime
from typing import Set
import requests
import re

from IGitt.GitHub import get, patch, post, delete, GitHubMixin, GH_INSTANCE_URL
from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubReaction import GitHubReaction
from IGitt.GitHub.GitHubReaction import PREVIEW_HEADER
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.Interfaces.Comment import CommentType
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces import IssueStates


CLOSED_BY_PATTERN = re.compile('closed this(?:\n| )+in(?:\n| )+<a href=\"/(.+)/'
                               'pull/([0-9]+)\">#(?:[0-9]+)</a>')


class GitHubIssue(GitHubMixin, Issue):
    """
    This class represents an issue on GitHub.
    """

    def __init__(self, token: GitHubToken, repository: str, number: int):
        """
        Creates a new GitHubIssue with the given credentials.

        >>> from os import environ
        >>> issue = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/repo_that_doesnt_exist', 1)
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
         ...
        RuntimeError: ({'message': 'Not Found', ...}, 404)

        :param token: A GitHubToken object.
        :param repository: The full name of the repository,
                           e.g. ``sils/something``.
        :param number: The issue number.
        :raises RuntimeError: If something goes wrong (network, auth, ...)
        """
        self._token = token
        self._repository = repository
        self._number = number
        self._url = '/repos/'+repository+'/issues/'+str(number)

    @property
    def repository(self):
        """
        Returns the GitHub repository this issue is linked with as a
        GitHubRepository instance.
        """
        from IGitt.GitHub.GitHubRepository import GitHubRepository
        return GitHubRepository(self._token, self._repository)

    @property
    def title(self):
        """
        Retrieves the title of the issue.

        >>> from os import environ
        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
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
        return self.data['title']

    @title.setter
    def title(self, new_title):
        """
        Sets the title of the issue.

        :param new_title: The new title.
        """
        self.data = patch(self._token, self._url, {'title': new_title})

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
        return self._number

    @property
    def assignees(self) -> Set[GitHubUser]:
        """
        Retrieves the assignee of the issue:

        >>> from os import environ
        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 1)
        >>> {a.username for a in issue.assignees}
        {'gitmate-test-user'}

        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 2)
        >>> issue.assignees  # Returns empty set, unassigned
        {}

        :return: A set containing the usernames of assignees.
        """
        return set(
            GitHubUser.from_data(user, self._token, user['login'])
            for user in self.data['assignees']
        )

    @assignees.setter
    def assignees(self, value: Set[GitHubUser]):
        """
        Setter for ssignees.
        """
        if value - self.assignees:
            self.assign(*(value - self.assignees))

        if self.assignees - value:
            self.unassign(*(self.assignees - value))

    def assign(self, *users: Set[GitHubUser]):
        """
        Adds the user as one of the assignees of the issue.
        :param username: Username of the user to be added as an assignee.
        """
        url = self._url + '/assignees'
        self.data = post(self._token, url,
                         {'assignees': [user.username for user in users]})

    def unassign(self, *users: Set[GitHubUser]):
        """
        Removes the user from the assignees of the issue.
        :param users: Username of the user to be unassigned.
        """
        url = self._url + '/assignees'
        delete(self._token, url,
               {'assignees': [user.username for user in users]})
        self.data = get(self._token, self._url)

    @property
    def description(self):
        r"""
        Retrieves the main description of the issue:

        >>> from os import environ
        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 1)
        >>> issue.description
        'A nice description!\n'

        :return: A string containing the main description of the issue.
        """
        return self.data['body'] if self.data['body'] else ''

    @description.setter
    def description(self, new_description):
        """
        Sets the description of the issue.

        :param new_description: The new description.
        """
        self.data = patch(self._token,
                          self._url,
                          {'body': new_description})

    @property
    def author(self) -> GitHubUser:
        """
        Retrieves the author of the issue.

        :return: A GitHubUser object.
        """
        return GitHubUser.from_data(self.data['user'],
                                    self._token,
                                    self.data['user']['login'])

    def add_comment(self, body):
        """
        Adds a comment to the issue:

        >>> from os import environ
        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
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

        return GitHubComment.from_data(result, self._token, self._repository,
                                       CommentType.ISSUE, result['id'])

    @property
    def comments(self):
        r"""
        Retrieves comments from the issue.

        >>> from os import environ
        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 9)
        >>> comments = issue.comments

        Now we can e.g. access the last comment:

        >>> comments[-1].body
        'Do not comment here.\n'

        :return: A list of Comment objects.
        """
        return [GitHubComment.from_data(result, self._token, self._repository,
                                        CommentType.ISSUE, result['id'])
                for result in get(self._token, self._url + '/comments')]

    @property
    def labels(self):
        """
        Retrieves all labels associated with this bug.

        >>> from os import environ
        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
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
        return set(label['name'] for label in self.data['labels'])

    @labels.setter
    def labels(self, value: Set[str]):
        """
        Sets the labels to the given set of labels.

        :param value: A set of label texts.
        """
        # Only if self.data is populated we actually save a request here
        if 'labels' in self.data and value == self.labels:
            return  # No need to patch

        self.data = patch(self._token, self._url, {'labels': list(value)})

    @property
    def available_labels(self):
        """
        Retrieves a set of captions that are available for labelling bugs.

        >>> from os import environ
        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
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
        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 1)
        >>> issue.created
        datetime.datetime(2016, 1, 13, 7, 56, 23)
        """
        return datetime.strptime(self.data['created_at'],
                                 '%Y-%m-%dT%H:%M:%SZ')

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the issue was updated the last time.

        >>> from os import environ
        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 9)
        >>> issue.updated
        datetime.datetime(2016, 10, 9, 11, 27, 11)
        """
        return datetime.strptime(self.data['updated_at'],
                                 '%Y-%m-%dT%H:%M:%SZ')

    def close(self):
        """
        Closes the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = patch(self._token, self._url, {'state': 'closed'})

    def reopen(self):
        """
        Reopens the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = patch(self._token, self._url, {'state': 'open'})

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
        >>> issue = GitHubIssue(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 10)
        >>> issue.state
        <IssueStates.OPEN: 'open'>
        >>> str(issue.state)
        'open'

        So if we close it:

        >>> issue.close()
        >>> issue.state
        <IssueStates.CLOSED: 'closed'>
        >>> str(issue.state)
        'closed'

        And reopen it:

        >>> issue.reopen()
        >>> issue.state
        <IssueStates.OPEN: 'open'>

        :return: Either <IssueStates.OPEN: 'open'> or
        <IssueStates.CLOSED: 'closed'>.
        """
        return IssueStates[self.data['state'].upper()]

    @property
    def reactions(self) -> Set[GitHubReaction]:
        """
        Retrieves the reactions / award emojis applied on the issue.
        """
        url = self._url + '/reactions'
        reactions = get(self._token, url, headers=PREVIEW_HEADER)
        return {GitHubReaction.from_data(r, self._token, self, r['id'])
                for r in reactions}

    @staticmethod
    def create(token: str, repository: str,
               title: str, body: str=''):
        """
        Create a new issue with given title and body.

        >>> from os import environ
        >>> issue = GitHubIssue.create(
        ...     GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...     'gitmate-test-user/test',
        ...     'test issue title',
        ...     'sample description'
        ... )
        >>> issue.state
        <IssueStates.OPEN: 'open'>
        >>> str(issue.state)
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
            'title': title,
            'body': body,
        }

        resp = post(token, post_url, data)
        issue_number = resp['number']

        return GitHubIssue.from_data(resp, token, repository, issue_number)

    @property
    def mrs_closed_by(self):
        """
        Returns the merge requests that close this issue.
        """
        from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest

        r = requests.get(GH_INSTANCE_URL + self._url.replace('/repos', ''))

        matches = CLOSED_BY_PATTERN.findall(r.text)

        return {GitHubMergeRequest(self._token, repo_name, int(number))
                for repo_name, number in matches}
