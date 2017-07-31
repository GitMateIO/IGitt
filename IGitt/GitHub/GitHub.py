"""
Contains the Hoster implementation for GitHub.
"""

from IGitt.GitHub import get, GitHubToken
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.Interfaces.Actions import IssueActions, MergeRequestActions, \
    PipelineActions
from IGitt.Interfaces.Comment import CommentType
from IGitt.Interfaces.Hoster import Hoster
from IGitt.GitHub.GitHubRepository import GitHubRepository


class GitHub(Hoster):
    """
    A high level interface to GitHub.
    """

    def __init__(self, token: GitHubToken):
        """
        Creates a new GitHub Hoster object.

        :param token: A GitHubToken object to use for authentication.
        """
        self._token = token

    @property
    def master_repositories(self):
        """
        Retrieves repositories the user has admin access to.
        """
        repo_list = get(self._token, '/user/repos')
        return {GitHubRepository(self._token, repo['full_name'])
                for repo in repo_list if repo['permissions']['admin']}

    @property
    def owned_repositories(self):
        """
        Retrieves repositories owned by the authenticated user.

        >>> from os import environ
        >>> github = GitHub(GitHubToken(environ['GITHUB_TEST_TOKEN']))
        >>> sorted(map(lambda x: x.full_name, github.owned_repositories))
        ['gitmate-test-user/test']

        :return: A set of full repository names.
        """
        repo_list = get(self._token, '/user/repos', {'affiliation': 'owner'})
        return {GitHubRepository(self._token, repo['full_name'])
                for repo in repo_list}

    @property
    def write_repositories(self):
        """
        Retrieves the full names of repositories this user can write to.

        >>> from os import environ
        >>> github = GitHub(GitHubToken(environ['GITHUB_TEST_TOKEN']))
        >>> sorted(map(lambda x: x.full_name, github.write_repositories))
        ['gitmate-test-user/test', 'sils/gitmate-test']

        :return: A set of strings.
        """
        repo_list = get(self._token, '/user/repos')
        return {GitHubRepository(self._token, repo['full_name'])
                for repo in repo_list if repo['permissions']['push']}

    def get_repo(self, repository) -> GitHubRepository:
        """
        Retrieve a given repository.

        >>> from os import environ
        >>> github = GitHub(environ['GITHUB_TEST_TOKEN'])
        >>> repo = github.get_repo('gitmate-test-user/test')
        >>> isinstance(repo, GitHubRepository)
        True

        :return: A repository object.
        """
        return GitHubRepository(self._token, repository)

    def handle_webhook(self, event: str, data: dict):
        """
        Handles a GitHub webhook for you.

        If it's an issue event it returns e.g.
        ``IssueActions.OPENED, [GitHubIssue(...)]``, for comments it returns
        ``MergeRequestActions.COMMENTED,
        [GitHubMergeRequest(...), GitHubComment(...)]``.

        :param event: The HTTP_X_GITHUB_EVENT of the request header.
        :param data:  The pythonified JSON data of the request.
        :return:      An IssueActions or MergeRequestActions member and a list
                      of the affected IGitt objects.
        """
        repository = data['repository']

        if event == 'issues':
            issue = data['issue']
            issue_obj = GitHubIssue(
                self._token, repository['full_name'], issue['number'])
            trigger_event = {
                'opened': IssueActions.OPENED,
                'closed': IssueActions.CLOSED,
                'reopened': IssueActions.REOPENED,
            }.get(data['action'], IssueActions.ATTRIBUTES_CHANGED)

            return trigger_event, [issue_obj]

        if event == 'pull_request':
            pull_request = data['pull_request']
            pull_request_obj = GitHubMergeRequest(
                self._token, repository['full_name'], pull_request['number'])
            trigger_event = {
                'synchronize': MergeRequestActions.SYNCHRONIZED,
                'opened': MergeRequestActions.OPENED,
            }.get(data['action'], MergeRequestActions.ATTRIBUTES_CHANGED)

            return trigger_event, [pull_request_obj]

        if event == 'issue_comment':
            if data['action'] != 'deleted':
                comment_obj = GitHubComment(
                    self._token,
                    repository['full_name'],
                    CommentType.MERGE_REQUEST,
                    data['comment']['id'])

                if 'pull_request' in data['issue']:
                    return MergeRequestActions.COMMENTED, [GitHubMergeRequest(
                        self._token,
                        repository['full_name'],
                        data['issue']['number']
                    ), comment_obj]

                return IssueActions.COMMENTED, [GitHubIssue(
                    self._token,
                    repository['full_name'],
                    data['issue']['number']
                ), comment_obj]

        if event == 'status':
            commit = data['commit']
            commit_obj = GitHubCommit(self._token, repository['full_name'],
                                      commit['sha'])
            return PipelineActions.UPDATED, [commit_obj]

        raise NotImplementedError('Given webhook cannot be handled yet.')
