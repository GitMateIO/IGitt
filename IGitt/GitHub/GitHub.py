"""
Contains the Hoster implementation for GitHub.
"""
import re

from IGitt.GitHub import get, GitHubToken, GitHubMixin
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubInstallation import GitHubInstallation
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.Interfaces.Actions import IssueActions, MergeRequestActions, \
    PipelineActions, InstallationActions
from IGitt.Interfaces.Comment import CommentType
from IGitt.Interfaces.Hoster import Hoster


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
        return {GitHubRepository.from_data(repo, self._token, repo['full_name'])
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
        return {GitHubRepository.from_data(repo, self._token, repo['full_name'])
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
        return {GitHubRepository.from_data(repo, self._token, repo['full_name'])
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

    @staticmethod
    def raw_search(token, raw_query):
        """
        Handles a GitHub search.

        Search syntax reference at
        https://help.github.com/articles/understanding-the-search-syntax/

        :param token:        A GitHubToken object to use for authentication.
        :param raw_query:    A string with the search query following syntax.
        :yields:             Search results as GitHubIssue(...) and
                             GitHubMergeRequest(...) objects for Issues and
                             Merge Requests respectively.
        """
        base_url = '/search/issues'
        query_params = {'q': raw_query,
                        'per_page': '100'}
        resp = get(token, base_url, query_params)

        issue_url_re = re.compile(
            r'https://(?:.+)/(\S+)/(\S+)/(issues|pull)/(\d+)')
        for item in resp:
            user, repo, item_type, item_number = issue_url_re.match(
                item['html_url']).groups()
            if item_type == 'issues':
                yield GitHubIssue.from_data(item, token, user + '/' + repo,
                                            int(item_number))
            elif item_type == 'pull':
                yield GitHubMergeRequest.from_data(item, token,
                                                   user + '/' + repo,
                                                   int(item_number))

    def _handle_webhook_installation(self, data):
        """Handles 'installation' event."""
        installation = data['installation']
        installation_obj = GitHubInstallation.from_data(
            installation, self._token, installation['id'])
        trigger_event = {
            'created': InstallationActions.CREATED,
            'deleted': InstallationActions.DELETED
        }[data['action']]

        # sender is the user who made this installation and has access to it
        sender = GitHubUser.from_data(data['sender'],
                                      self._token,
                                      data['sender']['login'])

        # When a new installation is created, it will be installed on at
        # least one repository which will be forwarded through
        # `repositories` key.
        if 'repositories' in data:
            repos = [
                GitHubRepository.from_data(repo, self._token, repo['id'])
                for repo in data['repositories']
            ]
            yield trigger_event, [installation_obj, sender, repos]
        else:
            yield trigger_event, [installation_obj, sender]

    def _handle_webhook_installation_repositories(self, data):
        """Handles 'installation_repositories' event."""
        installation = data['installation']
        installation_obj = GitHubInstallation.from_data(
            installation, self._token, installation['id'])

        # sender is the user who has access to this installation
        sender = GitHubUser.from_data(data['sender'],
                                      self._token,
                                      data['sender']['login'])

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

        yield trigger_event, [installation_obj, sender, repos]

    def _handle_webhook_issues(self, data, repository):
        """Handles 'issues' event."""
        issue = data['issue']
        issue_obj = GitHubIssue.from_data(
            issue, self._token, repository, issue['number'])
        trigger_event = {
            'opened': IssueActions.OPENED,
            'closed': IssueActions.CLOSED,
            'reopened': IssueActions.REOPENED,
            'labeled': IssueActions.LABELED,
            'unlabeled': IssueActions.UNLABELED,
        }.get(data['action'], IssueActions.ATTRIBUTES_CHANGED)

        if (trigger_event is IssueActions.LABELED
                or trigger_event is IssueActions.UNLABELED):
            yield trigger_event, [issue_obj, data['label']['name']]
        else:
            yield trigger_event, [issue_obj]

    def _handle_webhook_pull_request(self, data, repository):
        """Handles 'pull_request' event."""
        pull_request = data['pull_request']
        pull_request_obj = GitHubMergeRequest.from_data(
            pull_request, self._token, repository, pull_request['number'])
        trigger_event = {
            'synchronize': MergeRequestActions.SYNCHRONIZED,
            'opened': MergeRequestActions.OPENED,
            'closed': MergeRequestActions.CLOSED,
            'labeled': MergeRequestActions.LABELED,
            'unlabeled': MergeRequestActions.UNLABELED,
        }.get(data['action'], MergeRequestActions.ATTRIBUTES_CHANGED)
        if (
                trigger_event == MergeRequestActions.CLOSED and
                pull_request['merged'] is True):
            trigger_event = MergeRequestActions.MERGED

        if (trigger_event is MergeRequestActions.LABELED
                or trigger_event is MergeRequestActions.UNLABELED):
            yield trigger_event, [pull_request_obj, data['label']['name']]
        else:
            yield trigger_event, [pull_request_obj]

    def _handle_webhook_issue_comment(self, data, repository):
        """Handles 'issue_comment' event."""
        if data['action'] != 'deleted':
            comment_obj = GitHubComment.from_data(
                data['comment'],
                self._token,
                repository,
                CommentType.MERGE_REQUEST,
                data['comment']['id'])

            if 'pull_request' in data['issue']:
                yield (MergeRequestActions.COMMENTED,
                       [GitHubMergeRequest.from_data(
                           data['issue'],
                           self._token,
                           repository,
                           data['issue']['number']),
                        comment_obj])
            else:
                yield IssueActions.COMMENTED, [GitHubIssue.from_data(
                    data['issue'],
                    self._token,
                    repository,
                    data['issue']['number']
                ), comment_obj]

    def _handle_webhook_status(self, data, repository):
        """Handles 'status' event."""
        commit = data['commit']
        commit_obj = GitHubCommit.from_data(
            commit, self._token, repository, commit['sha'])
        yield PipelineActions.UPDATED, [commit_obj]

    def handle_webhook(self, event: str, data: dict):
        """
        Handles a GitHub webhook for you.

        If it's an issue event it returns e.g.
        ``IssueActions.OPENED, [GitHubIssue(...)]``, for comments it returns
        ``MergeRequestActions.COMMENTED,
        [GitHubMergeRequest(...), GitHubComment(...)]``, for updates it returns
        ``IssueActions.LABELED, [GitHubIssue(...), 'new label'].

        :param event:       The X_GITHUB_EVENT of the request header.
        :param data:        The pythonified JSON data of the request.
        :yields:            An IssueActions or MergeRequestActions member and a
                            list of the affected IGitt objects.
        """
        try:
            handler = getattr(self, '_handle_webhook_' + event)
        except AttributeError:
            raise NotImplementedError('Given webhook event cannot be handled '
                                      'yet.')
        if 'installation' in event:
            yield from handler(data)
        else:
            repository = self.get_repo_name(data)
            yield from handler(data, repository)
