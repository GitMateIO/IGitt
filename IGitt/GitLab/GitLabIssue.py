"""
This contains the Issue implementation for GitLab.
"""
from datetime import datetime
from typing import List
from typing import Set
from typing import Union
from urllib.parse import quote_plus

from IGitt.GitLab import get, put, post, delete, GitLabMixin
from IGitt.GitLab import GitLabOAuthToken, GitLabPrivateToken
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabReaction import GitLabReaction
from IGitt.GitLab.GitLabUser import GitLabUser
from IGitt.Interfaces.Comment import CommentType
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces import IssueStates
from IGitt.Interfaces import MergeRequestStates


class GitLabIssue(GitLabMixin, Issue):
    """
    This class represents an issue on GitLab.
    """

    def __init__(self, token: Union[GitLabOAuthToken, GitLabPrivateToken],
                 repository: str, number: int):
        """
        Creates a new GitLabIssue with the given credentials.

        >>> from os import environ
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                     'gitmate-test-user/repo_that_doesnt_exist', 1)
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        RuntimeError: ({'message': 'Not Found', ...}, 404)

        :param token: A Token object to be used for authentication.
        :param repository: The full name of the repository.
                           e.g. ``sils/baritone``.
        :param number: The issue internal identification number.
        :raises RuntimeError: If something goes wrong (network, auth, ...)
        """
        self._token = token
        self._repository = repository
        self._iid = number
        self._url = '/projects/{repo}/issues/{issue_iid}'.format(
            repo=quote_plus(repository), issue_iid=number)

    @property
    def repository(self):
        """
        Returns the GitLab repository this issue is linked with as a
        GitLabRepository instance.
        """
        from IGitt.GitLab.GitLabRepository import GitLabRepository
        return GitLabRepository(self._token, self._repository)

    @property
    def title(self) -> str:
        """
        Retrieves the title of the issue.

        >>> from os import environ
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
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
        return self.data['title']

    @title.setter
    def title(self, new_title):
        """
        Sets the title of the issue.

        :param new_title: The new title.
        """
        self.data = put(self._token, self._url, {'title': new_title})

    @property
    def number(self) -> int:
        """
        Returns the issue "number" or id.

        >>> from os import environ
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 1)
        >>> issue.number
        1

        :return: The number of the issue.
        """
        return self._iid

    @property
    def assignees(self):
        """
        Retrieves the assignee of the issue:

        >>> from os import environ
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 1)
        >>> issue.assignees
        {'gitmate-test-user'}

        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 2)
        >>> issue.assignees # Returns empty set, unassigned
        {}

        :return: A set containing the usernames of assignees.
        """
        return {GitLabUser.from_data(user, self._token, user['id'])
                for user in self.data['assignees']}

    def assign(self, *usernames: List[GitLabUser]):
        """
        Adds the user as one of the assignees of the issue.
        :param users: User objects of the users to be added as an assignee.
        """
        self.assignees |= set(usernames)

    def unassign(self, *users: List[GitLabUser]):
        """
        Removes the user from the assignees of the issue.
        :param users: User objects of the users to be unassigned.
        """
        self.assignees = self.assignees - set(users)

    @assignees.setter
    def assignees(self, value: Set[GitLabUser]):
        """
        Setter for assignees.
        """
        self.data = put(self._token, self._url,
                        {'assignee_ids': [u.identifier for u in value]})

    @property
    def description(self) -> str:
        r"""
        Retrieves the main description of the issue.

        >>> from os import environ
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 1)
        >>> issue.description
        'I am a serious issue. Fix me soon, dude.'

        :return: A string containing the main description of the issue.
        """
        return self.data['description'] if self.data['description'] else ''

    @description.setter
    def description(self, new_description):
        """
        Sets the description of the issue.

        :param new_description: The new description.
        """
        self.data = put(self._token,
                        self._url,
                        {'description': new_description})

    @property
    def author(self) -> GitLabUser:
        """
        Retrieves the author of the issue.

        :return: A GitLabUser object.
        """
        return GitLabUser.from_data(self.data['author'],
                                    self._token,
                                    self.data['author']['id'])

    def add_comment(self, body):
        """
        Adds a comment to the issue.

        >>> from os import environ
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
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
    def comments(self) -> List[GitLabComment]:
        r"""
        Retrieves comments from the issue.

        As of now, the list of comments is not sorted. Related issue on GitLab
        CE here - https://gitlab.com/gitlab-org/gitlab-ce/issues/32057

        >>> from os import environ
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 3)
        >>> comments = issue.comments
        >>> for comment in comments:
        ...     print(comment.body)
        Stop staring at me.
        Go, get your work done.

        :return: A list of Comment objects.
        """
        return [
            GitLabComment.from_data(
                result, self._token, self._repository, self.number,
                CommentType.ISSUE, result['id']
            )
            for result in get(self._token, self._url + '/notes')
        ]

    @property
    def labels(self) -> Set[str]:
        """
        Retrieves all labels associated with this bug.

        >>> from os import environ
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
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
        return set(self.data['labels'])

    @labels.setter
    def labels(self, value: Set[str]):
        """
        Sets the value of labels to the given set of labels.

        :param value: A set of label texts.
        """
        # Only if self.data is populated we actually save a request here
        if 'labels' in self.data and value == self.labels:
            return  # No need to patch

        self.data = put(self._token, self._url,
                        {'labels': ','.join(map(str, value))})

    @property
    def available_labels(self) -> Set[str]:
        """
        Retrieves a set of captions that are available for labelling bugs.

        >>> from os import environ
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
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
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 4)
        >>> issue.created
        datetime.datetime(2017, 6, 5, 9, 45, 20, 678000)
        """
        return datetime.strptime(self.data['created_at'],
                                 '%Y-%m-%dT%H:%M:%S.%fZ')

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the issue was updated the last time.

        >>> from os import environ
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 4)
        >>> issue.updated
        datetime.datetime(2017, 6, 5, 9, 45, 56, 115000)
        """
        return datetime.strptime(self.data['updated_at'],
                                 '%Y-%m-%dT%H:%M:%S.%fZ')

    def close(self):
        """
        Closes the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = put(self._token, self._url, {'state_event': 'close'})

    def reopen(self):
        """
        Reopens the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = put(self._token, self._url, {'state_event': 'reopen'})

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
        >>> issue = GitLabIssue(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 1)
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

        Note: GitLab Issues & Merge Requests API underwent a change to have
        only two states, <IssueStates.OPEN: 'open'> or
        <IssueStates.CLOSED: 'closed'>. No 'reopened' state anymore.

        :return: Either <IssueStates.OPEN: 'open'> or
        <IssueStates.CLOSED: 'closed'>.
        """
        if self.data['state'] == 'opened':
            self.data['state'] = 'open'

        return IssueStates[self.data['state'].upper()]

    @property
    def reactions(self) -> Set[GitLabReaction]:
        """
        Retrieves the reactions / award emojis applied on the issue.
        """
        url = self._url + '/award_emoji'
        reactions = get(self._token, url)
        return {GitLabReaction.from_data(r, self._token, self, r['id'])
                for r in reactions}

    @staticmethod
    def create(token: Union[GitLabOAuthToken, GitLabPrivateToken],
               repository: str,
               title: str, body: str=''):
        """
        Create a new issue with given title and body.

        >>> from os import environ
        >>> issue = GitLabIssue.create(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test',
        ...     'test issue title',
        ...     'sample description'
        ... )
        >>> issue.state
        <IssueStates.OPEN: 'open'>

        Delete the issue to avoid filling the test repo with issues.

        >>> issue.delete()

        :return: GitLabIssue object of the newly created issue.
        """
        url = '/projects/{repo}/issues'.format(repo=quote_plus(repository))
        issue = post(token, url, {'title': title, 'description': body})

        return GitLabIssue.from_data(issue, token, repository, issue['iid'])

    @property
    def mrs_closed_by(self):
        """
        Returns the merge requests that close this issue.
        """
        from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest

        url = '{url}/closed_by'.format(url=self._url)
        mrs = get(self._token, url)

        return {GitLabMergeRequest.from_data(mr,
                                             self._token,
                                             self._repository,
                                             mr['iid'])
                for mr in mrs if mr['state'] == MergeRequestStates.MERGED.value}
