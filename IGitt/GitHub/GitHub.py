"""
Contains the Hoster implementation for GitHub.
"""

from IGitt.GitHub import get, GitHubToken, GitHubMixin
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubInstallation import GitHubInstallation
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.Interfaces.Actions import IssueActions, MergeRequestActions, \
    PipelineActions, InstallationActions
from IGitt.Interfaces.Comment import CommentType
from IGitt.Interfaces.Hoster import Hoster
from IGitt.GitHub.GitHubRepository import GitHubRepository


class GitHub(GitHubMixin, Hoster):
    """
    A high level interface to GitHub.
    """

    def __init__(self, token: GitHubToken):
        """
        Creates a new GitHub Hoster object.

        :param token: A GitHubToken object to use for authentication.
        """
        self._token = token
        self._url = '/'

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

    @staticmethod
    def get_repo_name(webhook: dict):
        """
        Retrieves the repository name from given webhook data.
        """
        return webhook['repository']['full_name']

    def handle_webhook(self, event: str, data: dict):
        """
        Handles a GitHub webhook for you.

        If it's an issue event it returns e.g.
        ``IssueActions.OPENED, [GitHubIssue(...)]``, for comments it returns
        ``MergeRequestActions.COMMENTED,
        [GitHubMergeRequest(...), GitHubComment(...)]``.

        :param event:       The HTTP_X_GITLAB_EVENT of the request header.
        :param data:        The pythonified JSON data of the request.
        :return:            An IssueActions or MergeRequestActions member and a
                            list of the affected IGitt objects.
        """
        if event == 'installation':
            installation = data['installation']
            installation_obj = GitHubInstallation.from_data(
                installation, self._token, installation['id'])
            trigger_event = {
                'created': InstallationActions.CREATED,
                'deleted': InstallationActions.DELETED
            }[data['action']]

            return trigger_event, [installation_obj]

        if event == 'installation_repositories':
            installation = data['installation']
            installation_obj = GitHubInstallation.from_data(
                installation, self._token, installation['id'])
            if data['action'] == 'added':
                trigger_event = InstallationActions.REPOSITORIES_ADDED
                repos = [
                    GitHubRepository.from_data(repo, self._token, repo['id'])
                    for repo in data['repositories_added']
                ]
            elif data['action'] == 'removed':
                trigger_event = InstallationActions.REPOSITORIES_REMOVED
                repos = [
                    GitHubRepository.from_data(repo, self._token, repo['id'])
                    for repo in data['repositories_removed']
                ]

            return trigger_event, [installation_obj, repos]

        repository = self.get_repo_name(data)

        if event == 'issues':
            issue = data['issue']
            issue_obj = GitHubIssue.from_data(
                issue, self._token, repository, issue['number'])
            trigger_event = {
                'opened': IssueActions.OPENED,
                'closed': IssueActions.CLOSED,
                'reopened': IssueActions.REOPENED,
            }.get(data['action'], IssueActions.ATTRIBUTES_CHANGED)

            return trigger_event, [issue_obj]

        if event == 'pull_request':
            pull_request = data['pull_request']
            pull_request_obj = GitHubMergeRequest.from_data(
                pull_request, self._token, repository, pull_request['number'])
            trigger_event = {
                'synchronize': MergeRequestActions.SYNCHRONIZED,
                'opened': MergeRequestActions.OPENED,
                'closed': MergeRequestActions.CLOSED,
            }.get(data['action'], MergeRequestActions.ATTRIBUTES_CHANGED)
            if (
                    trigger_event == MergeRequestActions.CLOSED and
                    pull_request['merged'] is True):
                trigger_event = MergeRequestActions.MERGED

            return trigger_event, [pull_request_obj]

        if event == 'issue_comment':
            if data['action'] != 'deleted':
                comment_obj = GitHubComment.from_data(
                    data['comment'],
                    self._token,
                    repository,
                    CommentType.MERGE_REQUEST,
                    data['comment']['id'])

                if 'pull_request' in data['issue']:
                    return (MergeRequestActions.COMMENTED,
                            [GitHubMergeRequest.from_data(
                                data['issue'],
                                self._token,
                                repository,
                                data['issue']['number']),
                             comment_obj])

                return IssueActions.COMMENTED, [GitHubIssue.from_data(
                    data['issue'],
                    self._token,
                    repository,
                    data['issue']['number']
                ), comment_obj]

        if event == 'status':
            commit = data['commit']
            commit_obj = GitHubCommit.from_data(
                commit, self._token, repository, commit['sha'])
            return PipelineActions.UPDATED, [commit_obj]

        raise NotImplementedError('Given webhook cannot be handled yet.')
