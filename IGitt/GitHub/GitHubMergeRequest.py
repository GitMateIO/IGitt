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

from IGitt.GitHub import get, put, GitHubToken
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces import MergeRequestStates


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
    def author(self) -> GitHubUser:
        """
        Retrieves the author of the merge request.

        :return: A GitHubUser object.
        """
        return GitHubUser.from_data(self.data['user'],
                                    self._token,
                                    self.data['user']['login'])

    @property
    def state(self) -> MergeRequestStates:
        """
        Retrieves the state of the Pull Request on GitHub.

        :return:    A MergeRequestStates object.
        """
        state = {
            'open': MergeRequestStates.OPEN,
            'closed': MergeRequestStates.CLOSED,
        }[self.data['state']]
        if self.data['merged_at'] and self.data['state'] == 'closed':
            return MergeRequestStates.MERGED
        return state

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
        if should_remove_source_branch or _gitlab_merge_when_pipeline_succeeds:
            raise NotImplementedError

        merge_options = {}
        if message:
            lines = message.splitlines()
            merge_options['commit_title'] = lines.pop(0)
            merge_options['commit_message'] = '\n'.join(lines).strip()
        if sha:
            merge_options['sha'] = sha
        if _github_merge_method:
            merge_options['merge_method'] = _github_merge_method

        put(self._token, self._mr_url + '/merge', merge_options)

        self.refresh()
