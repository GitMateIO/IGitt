"""
Contains a class representing the GitHub pull request.

Labels, Milestones, Assignees and Comments are an integral part of GitHubIssue
class. They have a rich unified way of handling issues and pull requests.

Reference
- https://developer.github.com/v3/pulls/#labels-assignees-and-milestones

The methods being used from GitHubIssue are:
- number
- assignee
- add_comment
- comments
- labels
- labels.setter
- available_labels
"""
from datetime import datetime
from functools import lru_cache

from IGitt.GitHub import get
from IGitt.GitHub import patch
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.Interfaces.MergeRequest import MergeRequest


# Issue is used as a Mixin, super() is never called by design!
class GitHubMergeRequest(MergeRequest, GitHubIssue):
    """
    A Pull Request on GitHub.
    """

    def __init__(self, oauth_token: str, repository: str, pr_number: int):
        """
        Creates a new Pull Request.

        :param oauth_token: The OAuth token to authenticate with.
        :param repository: The repository containing the PR.
        :param pr_number: The PR number.
        """
        self._token = oauth_token
        self._number = pr_number
        self._repository = repository
        self._url = '/repos/' + repository + '/pulls/' + str(pr_number)

    @property
    def title(self):
        """
        Retrieves the title of the pull request.

        >>> from os import environ
        >>> mr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 1)
        >>> mr.title
        'test issue'

        You can simply set it using the property setter:

        >>> mr.title = 'dont panic'
        >>> mr.title
        'dont panic'

        >>> mr.title = 'test issue'

        :return: The title of the pull request - as string.
        """
        return self.data['title']

    @title.setter
    def title(self, new_title):
        """
        Sets the title of the pull request.

        :param new_title: The new title.
        """
        self.data = patch(self._token, self._url, {'title': new_title})

    @property
    def description(self):
        r"""
        Retrieves the main description of the pull request:

        >>> from os import environ
        >>> mr = GitHubIssue(environ['GITHUB_TEST_TOKEN'],
        ...                     'gitmate-test-user/test', 1)
        >>> mr.description
        'A nice description!\n'

        :return: A string containing the main description of the pull request.
        """
        return self.data['body']

    @property
    def base(self):
        """
        Retrieves the base commit as a commit object.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.base.sha
        '674498fd415cfadc35c5eb28b8951e800f357c6f'

        :return: A Commit object.
        """
        return GitHubCommit(self._token, self._repository,
                            self.data['base']['sha'])

    @property
    def head(self):
        """
        Retrieves the head commit as a commit object.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.head.sha
        'f6d2b7c66372236a090a2a74df2e47f42a54456b'

        :return: A Commit object.
        """
        return GitHubCommit(self._token, self._repository,
                            self.data['head']['sha'])

    @property
    def base_branch_name(self) -> str:
        """
        Retrieves the base branch name of the merge request, i.e. the one it
        should be merged into.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.base_branch_name
        'master'

        :return: A string.
        """
        return self.data['base']['ref']

    @property
    def head_branch_name(self) -> str:
        """
        Retrieves the head branch name of the merge request, i.e. the one that
        will be merged.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.head_branch_name
        'gitmate-test-user-patch-2'

        :return: A string.
        """
        return self.data['head']['ref']

    @property
    @lru_cache(None)
    def commits(self):
        """
        Retrieves a tuple of commit objects that are included in the PR.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> [commit.sha for commit in pr.commits]
        ['f6d2b7c66372236a090a2a74df2e47f42a54456b']

        :return: A tuple of commit objects.
        """
        commits = get(self._token, self._url + '/commits')
        return tuple(GitHubCommit(self._token, self._repository, commit['sha'])
                     for commit in commits)

    @property
    def repository(self):
        """
        Retrieves the repository where this comes from.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.repository.full_name
        'gitmate-test-user/test'

        :return: The repository object.
        """
        from .GitHubRepository import GitHubRepository
        return GitHubRepository(self._token, self._repository)

    @property
    def affected_files(self):
        """
        Retrieves affected files from a GitHub pull request.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.affected_files
        {'README.md'}

        :return: A set of filenames.
        """
        files = get(self._token, self._url + '/files')
        return {file['filename'] for file in files}

    @property
    def diffstat(self):
        """
        Gets additions and deletions of a merge request.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.diffstat
        (2, 0)

        :return: An (additions, deletions) tuple.
        """
        return self.data['additions'], self.data['deletions']

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the merge request was created.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.created
        datetime.datetime(2016, 1, 24, 19, 47, 19)
        """
        return datetime.strptime(self.data['created_at'],
                                 "%Y-%m-%dT%H:%M:%SZ")

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the merge request was updated the last
        time.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.updated
        datetime.datetime(2017, 6, 7, 8, 42, 43)
        """
        return datetime.strptime(self.data['updated_at'],
                                 "%Y-%m-%dT%H:%M:%SZ")

    def close(self):
        """
        Closes the merge request.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = patch(self._token, self._url, {'state': 'closed'})

    def reopen(self):
        """
        Reopens the merge request.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = patch(self._token, self._url, {'state': 'open'})

    def delete(self):
        """
        GitHub doesn't allow deleting issues or pull requests.
        """
        raise NotImplementedError

    @property
    def state(self) -> str:
        """
        Get's the state of the merge request.

        >>> from os import environ
        >>> mr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 11)
        >>> mr.state
        'open'

        So if we close it:

        >>> mr.close()
        >>> mr.state
        'closed'

        And reopen it:

        >>> mr.reopen()
        >>> mr.state
        'open'

        :return: Either 'open' or 'closed'.
        """
        return self.data['state']

    @property
    def number(self) -> int:
        """
        Returns the MR "number" or id.

        >>> from os import environ
        >>> mr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 11)
        >>> mr.number
        11

        :return: The number of the issue.
        """
        return self._number
