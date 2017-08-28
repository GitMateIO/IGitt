"""
Contains a class representing the GitLab merge request.
"""
import re

from functools import lru_cache
from urllib.parse import quote_plus

from IGitt.GitLab import get, GitLabOAuthToken, GitLabPrivateToken, \
    GL_INSTANCE_URL
from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.Interfaces.MergeRequest import MergeRequest


# Issue is used as a Mixin, super() is never called by design!
class GitLabMergeRequest(GitLabIssue, MergeRequest):
    """
    A Merge Request on GitLab.
    """

    def __init__(self, token: (GitLabOAuthToken, GitLabPrivateToken),
                 repository: str, number: int):
        """
        Creates a new GitLabMergeRequest object.

        :param token: A Token object to be used for authentication.
        :param repository: The repository containing the MR.
        :param number: The unique internal identifier for GitLab MRs.
        """
        self._token = token
        self._repository = repository
        self._iid = number
        self._url = '/projects/{repo}/merge_requests/{iid}'.format(
            repo=quote_plus(repository), iid=self._iid)

    @property
    def url(self):
        """
        Returns the link/URL of the merge request.
        """
        return GL_INSTANCE_URL + '/{}/merge_requests/{}'.format(
            self._repository,
            self.number
        )

    @property
    def base_branch_name(self) -> str:
        """
        Retrieves the base branch name of the merge request, i.e. the one it
        should be merged into.

        :return: A string.
        """
        return self.data['target_branch']

    @property
    def base(self) -> GitLabCommit:
        """
        Retrieves the base commit as a GitLabCommit object.

        >>> from os import environ
        >>> pr = GitLabMergeRequest(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test', 2
        ... )
        >>> pr.base.sha
        '198dd16f8249ea98ed41876efe27d068b69fa215'

        :return: A GitLabCommit object.
        """
        return GitLabCommit(self._token, self._repository, sha=None,
                            branch=quote_plus(self.base_branch_name))

    @property
    def head_branch_name(self) -> str:
        """
        Retrieves the head branch name of the merge request, i.e. the one which
        should be merged.

        :return: A string.
        """
        return self.data['source_branch']

    @property
    def head(self) -> GitLabCommit:
        """
        Retrieves the head commit as a GitLabCommit object.

         >>> from os import environ
        >>> pr = GitLabMergeRequest(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test', 2
        ... )
        >>> pr.head.sha
        '99f484ae167dcfcc35008ba3b5b564443d425ee0'

        :return: A GitLabCommit object.
        """
        return GitLabCommit(self._token, self._repository, sha=None,
                            branch=quote_plus(self.head_branch_name))

    @property
    @lru_cache(None)
    def commits(self):
        """
        Retrieves a tuple of commit objects that are included in the PR.

        >>> from os import environ
        >>> pr = GitLabMergeRequest(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test', 2
        ... )
        >>> assert ([commit.sha for commit in pr.commits] == [
        ...     '99f484ae167dcfcc35008ba3b5b564443d425ee0',
        ...     'bbd11b50412d34072f1889e4cea04a32de183605'])

        :return: A tuple of commit objects.
        """
        commits = get(self._token, self._url + '/commits')
        return tuple(GitLabCommit(self._token, self._repository, commit['id'])
                     for commit in commits)

    @property
    def repository(self):
        """
        Retrieves the repository where this comes from.

        >>> from os import environ
        >>> pr = GitLabMergeRequest(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test', 2
        ... )
        >>> pr.repository.full_name
        'gitmate-test-user/test'

        :return: The repository object.
        """
        from .GitLabRepository import GitLabRepository
        return GitLabRepository(self._token, self._repository)

    @property
    def affected_files(self):
        """
        Retrieves affected files from a GitLab merge request.

        >>> from os import environ
        >>> pr = GitLabMergeRequest(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test', 2
        ... )
        >>> pr.affected_files
        {'README.md'}

        :return: A set of filenames.
        """
        changes = get(self._token, self._url + '/changes')['changes']
        return {change['old_path'] for change in changes}

    @property
    def diffstat(self):
        """
        Gets additions and deletions of a merge request.

        >>> from os import environ
        >>> pr = GitLabMergeRequest(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test', 2
        ... )
        >>> pr.diffstat
        (2, 0)

        :return: An (additions, deletions) tuple.
        """
        changes = get(self._token, self._url + '/changes')['changes']
        results = []
        expr = re.compile(r'@@ [0-9+,-]+ [0-9+,-]+ @@')
        for change in changes:
            diff = change['diff']
            start_index = expr.search(diff).end()
            results += diff[start_index:].split('\n')

        additions = len([line for line in results if line.startswith('+')])
        deletions = len([line for line in results if line.startswith('-')])

        return additions, deletions

    @property
    def closes_issues(self) -> {GitLabIssue}:
        """
        Returns a set of GitLabIssue objects which would be closed upon merging
        this pull request.
        """
        issues = self._get_closes_issues()
        return {GitLabIssue(self._token, repo_name, number)
                for number, repo_name in issues}
