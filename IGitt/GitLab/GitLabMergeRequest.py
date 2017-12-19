"""
Contains a class representing the GitLab merge request.
"""
from functools import lru_cache
from typing import Set
from typing import Union
from urllib.parse import quote_plus
import re

from IGitt.GitLab import get, put, GitLabOAuthToken, GitLabPrivateToken
from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabUser import GitLabUser
from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces import MergeRequestStates


# Issue is used as a Mixin, super() is never called by design!
class GitLabMergeRequest(GitLabIssue, MergeRequest):
    """
    A Merge Request on GitLab.
    """

    def __init__(self, token: Union[GitLabOAuthToken, GitLabPrivateToken],
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
        return GitLabCommit(self._token, self.source_repository.full_name,
                            sha=None, branch=quote_plus(self.head_branch_name))

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
    @lru_cache(None)
    def source_repository(self):
        """
        Retrieves the repository where this PR's head branch is located at.

        >>> from os import environ
        >>> pr = GitLabMergeRequest(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test', 2
        ... )
        >>> pr.source_repository.full_name
        'gitmate-test-user/test'

        :return: The repository object.
        """
        from .GitLabRepository import GitLabRepository
        return GitLabRepository(self._token,
                                str(self.data['source_project_id']))

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
            match = expr.search(diff)
            if not match: # for binary files match is None
                continue
            start_index = match.end()
            results += diff[start_index:].split('\n')

        additions = len([line for line in results if line.startswith('+')])
        deletions = len([line for line in results if line.startswith('-')])

        return additions, deletions

    @property
    def closes_issues(self) -> Set[GitLabIssue]:
        """
        Returns a set of GitLabIssue objects which would be closed upon merging
        this pull request.
        """
        issues = self._get_closes_issues()
        return {GitLabIssue(self._token, repo_name, number)
                for number, repo_name in issues}

    @property
    def mentioned_issues(self) -> Set[GitLabIssue]:
        """
        Returns a set of GitLabIssue objects which are related to the merge
        request.
        """
        issues = self._get_mentioned_issues()
        return {GitLabIssue(self._token, repo_name, number)
                for number, repo_name in issues}

    @property
    def author(self) -> GitLabUser:
        """
        Retrieves the author of the merge request.

        :return: A GitLabUser object.
        """
        return GitLabUser.from_data(self.data['author'],
                                    self._token,
                                    self.data['author']['id'])

    @property
    def assignees(self):
        # GitLab Merge Requests do not support multiple assignees.
        user = self.data['assignee']
        if not user:
            return set()
        return {GitLabUser.from_data(user, self._token, user['id'])}

    @assignees.setter
    def assignees(self, value: Set[GitLabUser]):
        """
        Setter for assignees.
        """
        if len(value) > 1:
            raise NotImplementedError(
                'GitLab does not support assigning multiple users to the same'
                'Merge Request.')

        # GitLab MR API unassigns all users when 0 is sent.
        # Reference: https://docs.gitlab.com/ee/api/merge_requests.html#update-mr
        user = value.pop().identifier if len(value) == 1 else 0
        self.data = put(self._token, self._url, {'assignee_id': user})

    @property
    def state(self) -> MergeRequestStates:
        """
        Retrieves the state of the Pull Request on GitHub.

        :return:    A MergeRequestStates object.
        """
        return {
            'opened': MergeRequestStates.OPEN,
            'closed': MergeRequestStates.CLOSED,
            'merged': MergeRequestStates.MERGED
        }[self.data['state']]

    def merge(self, message: str=None, sha: str=None,
              should_remove_source_branch: bool=False,
              _github_merge_method: str=None,
              _gitlab_merge_when_pipeline_succeeds: bool=False):
        """
        Merges the merge request.

        :param message:                     The commit message.
        :param sha:                         The commit sha that the HEAD must
                                            match in order to merge.
        :param should_remove_source_branch: Whether the source branch should be
                                            removed upon a successful merge.
        :param _github_merge_method:        On GitHub, the merge method to use
                                            when merging the MR. Can be one of
                                            `merge`, `squash` or `rebase`.
        :param _gitlab_wait_for_pipeline:   On GitLab, whether the MR should be
                                            merged immediately after the
                                            pipeline succeeds.
        :raises RuntimeError:        If something goes wrong (network, auth...).
        :raises NotImplementedError: If an unused parameter is passed.
        """
        if _github_merge_method:
            raise NotImplementedError

        merge_options = {}
        if message:
            merge_options['merge_commit_message'] = message
        if sha:
            merge_options['sha'] = sha
        if should_remove_source_branch:
            merge_options['should_remove_source_branch'] = \
                should_remove_source_branch
        if _gitlab_merge_when_pipeline_succeeds:
            merge_options['merge_when_pipeline_succeeds'] = \
                _gitlab_merge_when_pipeline_succeeds

        self.data = put(self._token, self._url + '/merge', merge_options)
