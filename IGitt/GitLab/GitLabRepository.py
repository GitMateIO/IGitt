"""
Contains the GitLab Repository implementation.
"""
from datetime import datetime
from typing import Optional
from typing import Set
from typing import Union
from urllib.parse import quote_plus

from IGitt import ElementAlreadyExistsError, ElementDoesntExistError
from IGitt.GitLab import delete, get, post, GitLabMixin
from IGitt.GitLab import GitLabOAuthToken, GitLabPrivateToken
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabOrganization import GitLabOrganization
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces import IssueStates
from IGitt.Interfaces import MergeRequestStates
from IGitt.Interfaces.Repository import Repository
from IGitt.Interfaces.Repository import WebhookEvents
from IGitt.Utils import eliminate_none


GL_WEBHOOK_TRANSLATION = {
    WebhookEvents.PUSH: 'push_events',
    WebhookEvents.ISSUE: 'issues_events',
    WebhookEvents.MERGE_REQUEST: 'merge_requests_events',
    WebhookEvents.COMMIT_COMMENT: 'note_events',
    WebhookEvents.MERGE_REQUEST_COMMENT: 'note_events',
    WebhookEvents.ISSUE_COMMENT: 'note_events',
}

GL_WEBHOOK_EVENTS = {'tag_push_events', 'job_events', 'pipeline_events',
                     'wiki_events'} | set(GL_WEBHOOK_TRANSLATION.values())

GL_MR_STATE_TRANSLATION = {MergeRequestStates.MERGED: 'merged',
                           MergeRequestStates.OPEN: 'opened',
                           MergeRequestStates.CLOSED: 'closed'}

GL_ISSUE_STATE_TRANSLATION = {IssueStates.OPEN: 'opened',
                              IssueStates.CLOSED: 'closed'}


def date_in_range(data,
                  created_after: Optional[datetime]=None,
                  created_before: Optional[datetime]=None,
                  updated_after: Optional[datetime]=None,
                  updated_before: Optional[datetime]=None):
    """
    Returns true if issue/MR is in the given range.
    """
    is_created_after = not created_after
    is_created_before = not created_before
    is_updated_after = not updated_after
    is_updated_before = not updated_before
    if created_after and data['created_at']>str(created_after):
        is_created_after = True
    if created_before and data['created_at']<str(created_before):
        is_created_before = True
    if updated_after and data['updated_at']>str(updated_after):
        is_updated_after = True
    if updated_before and data['updated_at']<str(updated_before):
        is_updated_before = True
    return (is_created_after and is_created_before and is_updated_after and
            is_updated_before)


class GitLabRepository(GitLabMixin, Repository):
    """
    Represents a repository on GitLab.
    """

    def __init__(self, token: Union[GitLabOAuthToken, GitLabPrivateToken],
                 repository: Union[str, int]):
        """
        Creates a new GitLabRepository object with the given credentials.

        :param token: A Token object to be used for authentication.
        :param repository: Full name or unique identifier of the repository,
                           e.g. ``sils/baritone``.
        """
        self._token = token
        self._repository = repository
        try:
            repository = int(repository)
            self._repository = None
            self._url = '/projects/{}'.format(repository)
        except ValueError:
            self._url = '/projects/' + quote_plus(repository)

    @property
    def identifier(self):
        """
        Returns the id of the repository.
        """
        return self.data['id']

    @property
    def top_level_org(self):
        """
        Returns the topmost organization, e.g. for `gitmate/open-source/IGitt`
        this is `gitmate`.
        """
        return GitLabOrganization(self._token,
                                  self.full_name.split('/', maxsplit=1)[0])

    @property
    def full_name(self) -> str:
        """
        Retrieves the full name of the repository, e.g. "sils/baritone".

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> repo.full_name
        'gitmate-test-user/test'

        :return: The full repository name as string.
        """
        return self._repository or self.data['path_with_namespace']

    @property
    def commits(self):
        """
        Retrieves the set of commits in this repository.

        :return: A set of GitLabCommit objects.
        """
        # Don't move to module, leads to circular imports
        from IGitt.GitLab.GitLabCommit import GitLabCommit

        return {GitLabCommit.from_data(commit,
                                       self._token,
                                       self.full_name,
                                       commit['id'])
                for commit in get(self._token,
                                  self._url + '/repository/commits')}

    @property
    def clone_url(self) -> str:
        """
        Retrieves the URL of the repository.

        >>> from os import environ as env
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> expected = 'https://{}@gitlab.com/gitmate-test-user/test.git'
        >>> assert repo.clone_url == expected.format(env['GITLAB_TEST_TOKEN'])

        :return: A URL that can be used to clone the repository with Git.
        """
        return self.data['http_url_to_repo'].replace(
            '://', '://oauth2:' + self._token.value + '@', 1)

    def get_labels(self) -> Set[str]:
        """
        Retrieves the labels of the repository.

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> sorted(repo.get_labels())
        ['a', 'b', 'c']

        :return: A set of strings containing the label captions.
        """
        return {label['name']
                for label in get(self._token, self._url + '/labels')}

    def create_label(self, name: str, color: str):
        """
        Creates a new label with the given color. For an example,
        see delete_label.

        If a label that already exists is attempted to be created, that throws
        an exception:

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> sorted(repo.get_labels())
        ['a', 'b', 'c']
        >>> repo.create_label('c', '#555555')
        Traceback (most recent call last):
         ...
        IGitt.ElementAlreadyExistsError: c already exists.

        :param name: The name of the label to create.
        :param color: A HTML color value with a leading #.
        :raises ElementAlreadyExistsError: If the label name already exists.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        if name in self.get_labels():
            raise ElementAlreadyExistsError(name + ' already exists.')

        self.data = post(
            self._token,
            self._url + '/labels',
            {'name': name, 'color': color}
        )

    def delete_label(self, name: str):
        """
        Deletes a label.

        Take a given repository:

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> sorted(repo.get_labels())
        ['a', 'b', 'c']

        Let's create a label 'd':

        >>> repo.create_label('d', '#555555')
        >>> sorted(repo.get_labels())
        ['a', 'b', 'c', 'd']

        >>> repo.delete_label('d')
        >>> sorted(repo.get_labels())
        ['a', 'b', 'c']

        If the label doesn't exist it won't get silently dropped - no! You will
        get an exception.

        >>> repo.delete_label('d')
        Traceback (most recent call last):
         ...
        IGitt.ElementDoesntExistError: d doesnt exist.

        :param name: The caption of the label to delete.
        :raises ElementDoesntExistError: If the label doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        if name not in self.get_labels():
            raise ElementDoesntExistError(name + ' doesnt exist.')

        delete(self._token, self._url + '/labels', {'name': name})

    def get_issue(self, issue_number: int) -> GitLabIssue:
        """
        Retrieves an issue:

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> repo.get_issue(1).title
        'Take it serious, son!'

        :param issue_number: The issue IID of the issue on GitLab.
        :return: An Issue object.
        :raises ElementDoesntExistError: If the issue doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        return GitLabIssue(self._token, self.full_name, issue_number)

    def get_mr(self, mr_number: int):
        """
        Retrieves an MR.

        :param mr_number: The MR IID of the merge_request on GitLab.
        :return: A MergeRequest object.
        :raises ElementDoesntExistError: If the MR doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
        return GitLabMergeRequest(self._token, self.full_name, mr_number)

    @property
    def hooks(self) -> Set[str]:
        """
        Retrieves all URLs this repository is hooked to.

        :return: Set of URLs (str).
        """
        hook_url = self._url + '/hooks'
        hooks = get(self._token, hook_url)

        return {hook['url'] for hook in hooks}

    def register_hook(self,
                      url: str,
                      secret: Optional[str]=None,
                      events: Optional[Set[WebhookEvents]]=None):
        """
        Registers a webhook to the given URL. Use it as simple as:

        >>> from os import environ
        >>> repo = GitLabRepository(environ['GITLAB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> repo.register_hook("http://some.url/in/the/world")

        It does nothing if the hook is already there:

        >>> repo.register_hook("http://some.url/in/the/world")

        To register a secret token with the webhook, simply add
        the secret param:

        >>> repo.register_hook("http://some.url/i/have/a/secret",
        ...     "mylittlesecret")

        To delete it simply run:

        >>> repo.delete_hook("http://some.url/in/the/world")
        >>> repo.delete_hook("http://some.url/i/have/a/secret")

        :param url: The URL to fire the webhook to.
        :param secret:
            An optional secret token to be registered with the webhook.
        :param events:
            The events for which the webhook is to be registered against.
            Defaults to all possible events.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        if url in self.hooks:
            return

        config = {
            'url': url,
            'enable_ssl_verification': False,
        }

        if secret:
            config['token'] = secret

        if events and len(events):
            config.update({GL_WEBHOOK_TRANSLATION[event]: True
                           for event in events})
        else:
            config.update({event: True for event in GL_WEBHOOK_EVENTS})

        self.data = post(self._token, self._url + '/hooks', config)

    def delete_hook(self, url: str):
        """
        Deletes all webhooks to the given URL.

        :param url: The URL to not fire the webhook to anymore.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        hook_url = self._url + '/hooks'
        hooks = get(self._token, hook_url)

        # Do not use self.hooks since id of the hook is needed
        for hook in hooks:
            if hook['url'] == url:
                delete(self._token, hook_url + '/' + str(hook['id']))

    def create_issue(self, title: str, body: str='') -> GitLabIssue:
        """
        Create a new issue in the repository.
        """
        return GitLabIssue.create(self._token, self.full_name, title, body)

    @property
    def merge_requests(self) -> set:
        """
        Retrieves a set of merge request objects.

        >>> from os import environ
        >>> repo = GitLabRepository(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test'
        ... )
        >>> len(repo.merge_requests)
        4
        """
        from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
        return {GitLabMergeRequest.from_data(res, self._token,
                                             self.full_name, res['iid'])
                for res in get(self._token, self._url + '/merge_requests')}

    def filter_issues(self, state: str='opened') -> set:
        """
        Filters the issues from the repository based on properties.

        :param state: 'opened' or 'closed' or 'all'.
        """
        return {GitLabIssue.from_data(res, self._token,
                                      self.full_name, res['iid'])
                for res in get(self._token,
                               self._url + '/issues',
                               {'state': state})}

    @property
    def issues(self) -> set:
        """
        Retrieves a set of issue objects.

        >>> from os import environ
        >>> repo = GitLabRepository(environ['GITLAB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> len(repo.issues)
        13
        """
        return self.filter_issues()

    def create_fork(self, organization: Optional[str]=None,
                    namespace: Optional[str]=None):
        """
        Create a fork of Repository
        """
        url = self._url + '/fork'
        data = {
            'id': self.full_name,
            'namespace': namespace
        }
        res = post(self._token, url=url, data=data)

        return GitLabRepository(self._token, res['path_with_namespace'])

    def create_file(self, path: str, message: str, content: str,
                    branch: Optional[str]=None, committer: Optional[str]=None,
                    author: Optional[dict]=None, encoding: Optional[str]=None):
        """
        Create a new file in Repository
        """
        url = self._url + '/repository/files/' + path
        data = {
            'file_path' : path,
            'commit_message' : message,
            'content' : content,
            'branch' : branch,
            'encoding' : encoding
        }

        if author:
            data['author_name'] = author['name']
            data['author_email'] = author['email']

        data = eliminate_none(data)
        post(token=self._token, url=url, data=data)

        from IGitt.GitLab.GitLabContent import GitLabContent
        return GitLabContent(self._token, self.full_name, path=path)

    def create_merge_request(self, title:str, base:str, head:str,
                             body: Optional[str]=None,
                             target_project_id: Optional[int]=None,
                             target_project: Optional[str]=None):
        """
        Create a new merge request in Repository
        """
        url = self._url + '/merge_requests'
        data = {
            'title' : title,
            'target_branch' : base,
            'source_branch' : head,
            'id' : quote_plus(self.full_name),
            'target_project_id' : target_project_id
        }
        json = post(self._token, url=url, data=data)

        from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
        return GitLabMergeRequest.from_data(json, self._token,
                                            repository=target_project,
                                            number=json['iid'])

    def delete(self):
        """
        Delete the Repository
        """
        delete(token=self._token, url=self._url)

    def _search(self,
                search_type,
                state: Union[MergeRequestStates, IssueStates, None]):
        """
        Retrives a list of all issues or merge requests.
        :param search_type: A string for type of object i.e. issues for issue
                            and merge_requests for merge requests.
        :param state: A string for MR/issue state (opened or closed)
        :return: List of issues/merge requests.
        """
        url = self._url + '/{}'.format(search_type)
        if state is None:
            return get(self._token, url)
        elif isinstance(state, IssueStates):
            state = GL_ISSUE_STATE_TRANSLATION[state]
        elif isinstance(state, MergeRequestStates):
            state = GL_MR_STATE_TRANSLATION[state]
        return get(self._token, url, {'state': state})

    def search_issues(self,
                      created_after: Optional[datetime]=None,
                      created_before: Optional[datetime]=None,
                      updated_after: Optional[datetime]=None,
                      updated_before: Optional[datetime]=None,
                      state: Optional[IssueStates] = None):
        """
        Searches for issues based on created and updated date.
        """
        for issue_data in filter(lambda data: date_in_range(data,
                                                            created_after,
                                                            created_before,
                                                            updated_after,
                                                            updated_before),
                                 self._search('issues', state)):
            issue = self.get_issue(issue_data['iid'])
            issue.data = issue_data
            yield issue

    def search_mrs(self,
                   created_after: Optional[datetime]=None,
                   created_before: Optional[datetime]=None,
                   updated_after: Optional[datetime]=None,
                   updated_before: Optional[datetime]=None,
                   state: Optional[MergeRequestStates]=None):
        """
        Searches for merge request based on created and updated date.
        """
        for mr_data in filter(lambda data: date_in_range(data,
                                                         created_after,
                                                         created_before,
                                                         updated_after,
                                                         updated_before),
                              self._search('merge_requests', state)):
            merge_request = self.get_mr(mr_data['iid'])
            merge_request.data = mr_data
            yield merge_request

    def get_permission_level(self, user) -> AccessLevel:
        """
        Retrieves the permission level for the specified user on this
        repository.
        """
        members = get(self._token, self._url + '/members')
        if user.username not in map(lambda m: m['username'], members):
            return (AccessLevel.CAN_VIEW
                    if self.data['visibility'] != 'private'
                    else AccessLevel.NONE)
        curr_member_idx = next(i for (i, d) in enumerate(members)
                               if d['username'] == user.username)
        return AccessLevel(members[curr_member_idx]['access_level'])
