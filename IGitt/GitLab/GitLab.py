"""
Contains the Hoster implementation for GitLab.
"""

import logging

from IGitt.GitLab import get, GitLabOAuthToken, GitLabPrivateToken
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


class GitLab(Hoster):
    """
    A high level interface to GitLab.
    """

    def __init__(self, token: (GitLabOAuthToken, GitLabPrivateToken)):
        """
        Creates a new GitLab Hoster object.

        :param token: A Token object to be used for authentication.
        """
        self._token = token

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

    def handle_webhook(self, event: str, data: dict):
        """
        Handles a GitHub webhook for you.

        If it's an issue event it returns e.g.
        ``IssueActions.OPENED, [GitLabIssue(...)]``, for comments it returns
        ``MergeRequestActions.COMMENTED,
        [GitLabMergeRequest(...), GitLabComment(...)]``.

        :param event: The HTTP_X_GITLAB_EVENT of the request header.
        :param data:  The pythonified JSON data of the request.
        :return:      An IssueActions or MergeRequestActions member and a list
                      of the affected IGitt objects.
        """
        repository = (data['project'] if 'project' in data.keys()
                      else data['object_attributes']['target'])

        if event == 'Issue Hook':
            issue = data['object_attributes']
            issue_obj = GitLabIssue(
                self._token, repository['path_with_namespace'], issue['iid'])
            trigger_event = {
                'open': IssueActions.OPENED,
                'close': IssueActions.CLOSED,
                'reopen': IssueActions.REOPENED,
            }.get(issue['action'], IssueActions.ATTRIBUTES_CHANGED)

            return trigger_event, [issue_obj]

        if event == 'Merge Request Hook':
            merge_request_data = data['object_attributes']
            merge_request_obj = GitLabMergeRequest(
                self._token,
                repository['path_with_namespace'],
                merge_request_data['iid'])
            trigger_event = {
                'update': MergeRequestActions.ATTRIBUTES_CHANGED,
                'open': MergeRequestActions.OPENED,
                'reopen': MergeRequestActions.REOPENED,
            }.get(merge_request_data['action'])

            # nasty workaround for finding merge request resync
            if 'oldrev' in merge_request_data:
                trigger_event = MergeRequestActions.SYNCHRONIZED

            # no such webhook event action implemented yet
            if not trigger_event:
                raise NotImplementedError('Unrecgonized action: ' + event +
                                          '/' + merge_request_data['action'])

            return trigger_event, [merge_request_obj]

        if event == 'Note Hook':
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
                                         repository['path_with_namespace'], iid)
                action = MergeRequestActions.COMMENTED
            elif comment_type == CommentType.ISSUE:
                iid = data['issue']['iid']
                iss = GitLabIssue(self._token, repository['path_with_namespace'], iid)
                action = IssueActions.COMMENTED
            else:
                raise NotImplementedError

            return action, [iss, GitLabComment(
                self._token, repository['path_with_namespace'], iid,
                comment_type, comment['id']
            )]

        if event == 'Pipeline Hook':
            return PipelineActions.UPDATED, [GitLabCommit(
                self._token,
                repository['path_with_namespace'],
                data['commit']['id'])]

        raise NotImplementedError('Given webhook cannot be handled yet.')
