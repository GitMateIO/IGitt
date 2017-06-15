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

from IGitt.GitHub import get
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.Interfaces.MergeRequest import MergeRequest


# Issue is used as a Mixin, super() is never called by design!
class GitHubMergeRequest(GitHubIssue, MergeRequest):
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
        self._mr_url = '/repos/' + repository + '/pulls/' + str(pr_number)
        self._url = '/repos/'+repository+'/issues/'+str(pr_number)

    def refresh(self):
        self.data = self._get_data()
        self.data.update(get(self._token, self._mr_url))

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
        commits = get(self._token, self._mr_url + '/commits')
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
        files = get(self._token, self._mr_url + '/files')
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
    def url(self):
        """
        Returns the link/URL of the issue.
        """
        return 'https://github.com/{}/pull/{}'.format(self._repository,
                                                      self.number)

    def delete(self):
        """
        GitHub doesn't allow deleting issues or pull requests.
        """
        raise NotImplementedError
