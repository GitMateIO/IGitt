"""
Contains the Hoster implementation for GitLab.
"""

from typing import Union
import logging

from IGitt.GitLab import get, GitLabOAuthToken, GitLabPrivateToken, GitLabMixin
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces.Actions import IssueActions, MergeRequestActions, \
    PipelineActions
from IGitt.Interfaces.Comment import CommentType
from IGitt.Interfaces.Hoster import Hoster
from IGitt.GitLab.GitLabRepository import GitLabRepository

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class GitLab(GitLabMixin, Hoster):
    """
    A high level interface to GitLab.
    """

    def __init__(self, token: Union[GitLabOAuthToken, GitLabPrivateToken]):
        """
        Creates a new GitLab Hoster object.

        :param token: A Token object to be used for authentication.
        """
        self._token = token
        self._url = '/'

    @property
    def master_repositories(self):
        """
        Retrieves repositories the user has admin access to.
        """
        repo_list = get(self._token, '/projects', {'membership': True})
        repos = []
        for repo in repo_list:
            perms = repo['permissions']
            project_access = perms['project_access'] or {}
            group_access = perms['group_access'] or {}
            access_level = max(project_access.get('access_level', 0),
                               group_access.get('access_level', 0))
            if access_level >= AccessLevel.ADMIN.value:
                repos.append(repo)
        return {GitLabRepository(self._token, repo['path_with_namespace'])
                for repo in repos}

    @property
    def owned_repositories(self):
        """
        Retrieves repositories owned by the authenticated user.

        >>> from os import environ
        >>> GitLab = GitLab(GitLabOAuthToken(viron['GITLAB_TEST_TOKEN']))
        >>> sorted(map(lambda x: x.full_name, GitLab.owned_repositories)
        {'gitmate-test-user/test'}

        :return: A set of GitLabRepository objects.
        """
        repo_list = get(self._token, '/projects', {'owned': True})
        return {GitLabRepository(self._token, repo['path_with_namespace'])
                for repo in repo_list}

    @property
    def write_repositories(self):
        """
        Retrieves the full names of repositories this user can write to.

        >>> from os import environ
        >>> GitLab = GitLab(GitLabOAuthToken(viron['GITLAB_TEST_TOKEN']))
        >>> sorted(map(lambda x: x.full_name, GitLab.write_repositories))
        ['gitmate-test-user/test', 'nkprince007/gitmate-test']

        :return: A set of GitLabRepository objects.
        """
        repo_list = get(self._token, '/projects', {'membership': True})
        repos = []
        for repo in repo_list:
            perms = repo['permissions']
            project_access = perms['project_access'] or {}
            group_access = perms['group_access'] or {}
            access_level = max(project_access.get('access_level', 0),
                               group_access.get('access_level', 0))
            if access_level >= AccessLevel.CAN_WRITE.value:
                repos.append(repo)
        return {GitLabRepository(self._token, repo['path_with_namespace'])
                for repo in repos}

    def get_repo(self, repository) -> GitLabRepository:
        """
        Retrieve a given repository.

        >>> from os import environ
        >>> GitLab = GitLab(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']))
        >>> repo = source.get_repo('gitmate-test-user/test')
        >>> isinstance(repo, GitLabRepository)
        True

        :return: A repository object.
        """
        return GitLabRepository(self._token, repository)

    @staticmethod
    def get_repo_name(webhook: dict):
        """
        Retrieves the repository name from given webhook data.
        """
        # Push, Tag, Issue, Note, Wiki Page and Pipeline Hooks
        if 'project' in webhook.keys():
            return webhook['project']['path_with_namespace']

        # Merge Request Hook
        if 'object_attributes' in webhook.keys():
            return webhook['object_attributes']['target']['path_with_namespace']

        # Build Hook
        if 'repository' in webhook.keys():
            ssh_url = webhook['repository']['git_ssh_url']
            return ssh_url[ssh_url.find(':') + 1: ssh_url.rfind('.git')]

    @staticmethod
    def raw_search(token: Union[GitLabPrivateToken, GitLabOAuthToken],
                   raw_query: str):
        """
        GitLab doesn't allow searching through raw queries.
        """
        raise NotImplementedError


    @staticmethod
    def _handle_labels(actions_enum: Union[IssueActions, MergeRequestActions],
                       obj_to_return: Union[GitLabIssue, GitLabMergeRequest],
                       data: dict):
        """
        Yields `LABELED` or `UNLABELED` actions for each label added or removed
        from given `Issue` or `MergeRequest`.
        """
        old_attrs = {label['title']
                     for label in
                     data['changes']['labels']['previous']}
        new_attrs = {label['title']
                     for label in
                     data['changes']['labels']['current']}

        # new labels added
        for label in new_attrs - old_attrs:
            yield actions_enum.LABELED, [obj_to_return, label]

        # labels removed
        for label in old_attrs - new_attrs:
            yield actions_enum.UNLABELED, [obj_to_return, label]


    def _handle_webhook_issue(self, data, repository):
        issue = data['object_attributes']
        issue_obj = GitLabIssue(
            self._token, repository, issue['iid'])
        trigger_event = {
            'open': IssueActions.OPENED,
            'close': IssueActions.CLOSED,
            'reopen': IssueActions.REOPENED,
        }.get(issue['action'], IssueActions.ATTRIBUTES_CHANGED)

        if (trigger_event == IssueActions.ATTRIBUTES_CHANGED and
                'labels' in data['changes']):
            # labels are changed
            yield from type(self)._handle_labels(
                IssueActions, issue_obj, data)
        else:
            yield trigger_event, [issue_obj]

    def _handle_webhook_merge_request(self, data, repository):
        merge_request_data = data['object_attributes']
        merge_request_obj = GitLabMergeRequest(
            self._token,
            repository,
            merge_request_data['iid'])
        trigger_event = {
            'update': MergeRequestActions.ATTRIBUTES_CHANGED,
            'open': MergeRequestActions.OPENED,
            'reopen': MergeRequestActions.REOPENED,
            'merge': MergeRequestActions.MERGED,
        }.get(merge_request_data['action'])

        # nasty workaround for finding merge request resync
        if 'oldrev' in merge_request_data:
            trigger_event = MergeRequestActions.SYNCHRONIZED


        # no such webhook event action implemented yet
        if not trigger_event:
            raise NotImplementedError('Unrecgonized action: Merge Request Hook'
                                      '/' + merge_request_data['action'])

        if (trigger_event is MergeRequestActions.ATTRIBUTES_CHANGED and
                'labels' in data['changes']):
            yield from type(self)._handle_labels(MergeRequestActions,
                                                 merge_request_obj, data)
        else:
            yield trigger_event, [merge_request_obj]

    def _handle_webhook_note(self, data, repository):
        comment = data['object_attributes']
        comment_type = {
            'MergeRequest': CommentType.MERGE_REQUEST,
            'Commit': CommentType.COMMIT,
            'Issue': CommentType.ISSUE,
            'Snippet': CommentType.SNIPPET
        }.get(comment['noteable_type'])

        if comment_type == CommentType.MERGE_REQUEST:
            iid = data['merge_request']['iid']
            iss = GitLabMergeRequest(self._token,
                                     repository, iid)
            action = MergeRequestActions.COMMENTED
        elif comment_type == CommentType.ISSUE:
            iid = data['issue']['iid']
            iss = GitLabIssue(self._token, repository, iid)
            action = IssueActions.COMMENTED
        else:
            raise NotImplementedError

        yield action, [iss, GitLabComment(
            self._token, repository, iid,
            comment_type, comment['id']
        )]

    def _handle_webhook_pipeline(self, data, repository):
        yield PipelineActions.UPDATED, [GitLabCommit(
            self._token,
            repository,
            data['commit']['id'])]

    def handle_webhook(self, event: str, data: dict):
        """
        Handles a GitLab webhook for you.

        If it's an issue event it returns e.g.
        ``IssueActions.OPENED, [GitLabIssue(...)]``, for comments it returns
        ``MergeRequestActions.COMMENTED,
        [GitLabMergeRequest(...), GitLabComment(...)]``, for updates it returns
        ``IssueActions.LABELED, [GitLabIssue(...), 'new label']``

        :param event:       The HTTP_X_GITLAB_EVENT of the request header.
        :param data:        The pythonified JSON data of the request.
        :yields:            An IssueActions or MergeRequestActions member and a
                            list of the affected IGitt objects.
        """
        repository = self.get_repo_name(data)
        part_handler_name = '_'.join(
            event.strip('Hook').strip().lower().split())

        try:
            handler = getattr(self, '_handle_webhook_' +  part_handler_name)
        except AttributeError:
            raise NotImplementedError('Given webhook cannot be handled yet.')
        else:
            yield from handler(data, repository)
