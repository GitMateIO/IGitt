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
from functools import lru_cache
from typing import Set

from IGitt.GitHub import get, GitHubToken
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.Interfaces.MergeRequest import MergeRequest


# Issue is used as a Mixin, super() is never called by design!
from IGitt.Utils import PossiblyIncompleteDict


class GitHubMergeRequest(GitHubIssue, MergeRequest):
    """
    A Pull Request on GitHub.
    """

    def __init__(self, token: GitHubToken, repository: str, number: int):
        """
        Creates a new Pull Request.

        :param token: A GitHubToken object to authenticate with.
        :param repository: The repository containing the PR.
        :param number: The PR number.
        """
        self._token = token
        self._number = number
        self._repository = repository
        self._mr_url = '/repos/' + repository + '/pulls/' + str(number)
        self._url = '/repos/'+repository+'/issues/'+str(number)

    def _get_data(self):
        issue_data = get(self._token, self._url)

        def get_full_data():
            """
            Updates the incomplete issue data with the PR data to make it
            complete.
            """
            # Ignore PyLintBear (E1101), its type inference is too stupid
            issue_data.update(get(self._token, self._mr_url))
            return issue_data

        # If issue data is sufficient, don't even get MR data
        return PossiblyIncompleteDict(issue_data, get_full_data)

    @property
    def base(self):
        """
        Retrieves the base commit as a commit object.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test', 7)
        >>> pr.base.sha
        '674498fd415cfadc35c5eb28b8951e800f357c6f'

        :return: A Commit object.
        """
        return GitHubCommit.from_data(self.data['base'], self._token,
                                      self._repository,
                                      self.data['base']['sha'])

    @property
    def head(self):
        """
        Retrieves the head commit as a commit object.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test', 7)
        >>> pr.head.sha
        'f6d2b7c66372236a090a2a74df2e47f42a54456b'

        :return: A Commit object.
        """
        return GitHubCommit.from_data(self.data['head'], self._token,
                                      self.repository.full_name,
                                      self.data['head']['sha'])

    @property
    def base_branch_name(self) -> str:
        """
        Retrieves the base branch name of the merge request, i.e. the one it
        should be merged into.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(GitHubToken(environ['GITHUB_TEST_TOKEN']),
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
        >>> pr = GitHubMergeRequest(GitHubToken(environ['GITHUB_TEST_TOKEN']),
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
        >>> pr = GitHubMergeRequest(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test', 7)
        >>> [commit.sha for commit in pr.commits]
        ['f6d2b7c66372236a090a2a74df2e47f42a54456b']

        :return: A tuple of commit objects.
        """
        commits = get(self._token, self._mr_url + '/commits')
        return tuple(GitHubCommit.from_data(commit, self._token,
                                            self._repository, commit['sha'])
                     for commit in commits)

    @property
    def repository(self):
        """
        Retrieves the repository where this comes from.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test', 7)
        >>> pr.repository.full_name
        'gitmate-test-user/test'

        :return: The repository object.
        """
        from .GitHubRepository import GitHubRepository
        return GitHubRepository(self._token, self._repository)

    @property
    def source_repository(self):
        """
        Retrieves the repository where this PR's head branch is located at.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test', 7)
        >>> pr.source_repository.full_name
        'gitmate-test-user/test'

        :return: The repository object.
        """
        from .GitHubRepository import GitHubRepository
        return GitHubRepository(self._token,
                                self.data['head']['repo']['full_name'])

    @property
    def affected_files(self):
        """
        Retrieves affected files from a GitHub pull request.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test', 7)
        >>> pr.affected_files
        {'README.md'}

        :return: A set of filenames.
        """
        files = get(self._token, self._mr_url + '/files')
        return {file['filename'] for file in files}

    @property
    def diffstat(self):
        """
        Gets additions and deletions of a merge request.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test', 7)
        >>> pr.diffstat
        (2, 0)

        :return: An (additions, deletions) tuple.
        """
        return self.data['additions'], self.data['deletions']

    def delete(self):
        """
        GitHub doesn't allow deleting issues or pull requests.
        """
        raise NotImplementedError

    @property
    def closes_issues(self) -> Set[GitHubIssue]:
        """
        Returns a set of GitHubIssue objects which would be closed upon merging
        this pull request.
        """
        issues = self._get_closes_issues()
        return {GitHubIssue(self._token, repo_name, number)
                for number, repo_name in issues}

    @property
    def mentioned_issues(self) -> Set[GitHubIssue]:
        """
        Returns a set of GitHubIssue objects which are related to the pull
        request.
        """
        issues = self._get_mentioned_issues()
        return {GitHubIssue(self._token, repo_name, number)
                for number, repo_name in issues}

    @property
    def author(self) -> str:
        """
        Returns the author of the PR.
        """
        return self.data['user']['login']
