"""
Contains a class representing the GitHub pull request.
"""
from datetime import datetime

from IGitt.GitHub import get
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.Interfaces.MergeRequest import MergeRequest


class GitHubMergeRequest(MergeRequest):
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
        self._repository = repository
        self._number = pr_number
        self._url = '/repos/' + repository + '/pulls/' + str(pr_number)
        self._data = get(self._token, self._url)

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
                            self._data['base']['sha'])

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
                            self._data['head']['sha'])

    @property
    def commits(self):
        """
        Retrieves a list of commit objects that are included in the PR.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> [commit.sha for commit in pr.commits]
        ['f6d2b7c66372236a090a2a74df2e47f42a54456b']

        :return: A list of commit objects.
        """
        commits = get(self._token, self._url + '/commits')
        return [GitHubCommit(self._token, self._repository, commit['sha'])
                for commit in commits]

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
    def issue(self):
        """
        Retrieves a GitHubIssue:

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.issue.labels
        set()

        :return: The issue object.
        """
        return GitHubIssue(self._token, self._repository, self._number)

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
        return self._data['additions'], self._data['deletions']

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
        return datetime.strptime(self._data['created_at'],
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
        datetime.datetime(2016, 1, 24, 19, 47, 45)
        """
        return datetime.strptime(self._data['updated_at'],
                                 "%Y-%m-%dT%H:%M:%SZ")
