"""
Contains the GitHub Repository implementation.
"""
from base64 import b64encode
from datetime import datetime
from typing import Optional
from typing import Set
from typing import Union

from IGitt import ElementAlreadyExistsError, ElementDoesntExistError
from IGitt.GitHub import delete, get, post, GitHubMixin, put
from IGitt.GitHub import GitHubToken
from IGitt.GitHub import GitHubInstallationToken
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubOrganization import GitHubOrganization
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces import IssueStates
from IGitt.Interfaces import MergeRequestStates
from IGitt.Interfaces.Repository import Repository
from IGitt.Interfaces.Repository import WebhookEvents
from IGitt.Utils import eliminate_none


GH_WEBHOOK_TRANSLATION = {
    WebhookEvents.PUSH: 'push',
    WebhookEvents.ISSUE: 'issues',
    WebhookEvents.MERGE_REQUEST: 'pull_request',
    WebhookEvents.COMMIT_COMMENT: 'commit_comment',
    WebhookEvents.MERGE_REQUEST_COMMENT: 'issue_comment',
    WebhookEvents.ISSUE_COMMENT: 'issue_comment'
}

GH_ISSUE_STATE_TRANSLATION = {
    'opened': 'open',
    'closed': 'closed',
    'all': 'all'
}


class GitHubRepository(GitHubMixin, Repository):
    """
    Represents a repository on GitHub.
    """

    def __init__(self,
                 token: [GitHubToken, GitHubInstallationToken],
                 repository: Union[str, int]):
        """
        Creates a new GitHubRepository object with the given credentials.

        :param token: A GitHubToken object to authenticate with.
        :param repository: Full name or unique identifier of the repository,
                           e.g. ``sils/something``.
        """
        self._token = token
        self._repository = repository
        try:
            repository = int(repository)
            self._repository = None
            self._url = '/repositories/{}'.format(repository)
        except ValueError:
            self._url = '/repos/'+repository

    @property
    def identifier(self) -> int:
        """
        Returns the identifier of the repository.
        """
        return self.data['id']

    @property
    def top_level_org(self):
        """
        Returns the topmost organization, e.g. for `gitmate/open-source/IGitt`
        this is `gitmate`.
        """
        return GitHubOrganization(self._token,
                                  self.full_name.split('/', maxsplit=1)[0])

    @property
    def full_name(self):
        """
        Retrieves the full name of the repository, e.g. "sils/something".

        >>> from os import environ
        >>> repo = GitHubRepository(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test')
        >>> repo.full_name
        'gitmate-test-user/test'

        :return: The full repository name as string.
        """
        return self._repository or self.data['full_name']

    @property
    def commits(self):
        """
        Retrieves the set of commits in this repository.

        :return: A set of GitHubCommit objects.
        """
        # Don't move to module, leads to circular imports
        from IGitt.GitHub.GitHubCommit import GitHubCommit

        try:
            return {GitHubCommit.from_data(commit,
                                           self._token,
                                           self.full_name,
                                           commit['sha'])
                    for commit in get(self._token, self._url + '/commits')}
        except RuntimeError as ex:
            # Repository is empty. GitHub returns 409.
            if ex.args[1] == 409:
                return set()
            raise ex  # dont cover, this is the real exception


    @property
    def clone_url(self):
        """
        Retrieves the URL of the repository.

        >>> from os import environ as env
        >>> repo = GitHubRepository(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test')
        >>> expected = 'https://{}@github.com/gitmate-test-user/test.git'
        >>> assert repo.clone_url == expected.format(GitHubToken(
        ...     env['GITHUB_TEST_TOKEN'])
        ... )

        :return: A URL that can be used to clone the repository with Git.
        """
        url = 'github.com'
        if isinstance(self._token, GitHubInstallationToken):
            # Reference: https://developer.github.com/apps/building-integrations/setting-up-and-registering-github-apps/about-authentication-options-for-github-apps/#http-based-git-access-by-an-installation
            return self.data['clone_url'].replace(
                url, 'x-access-token:%s@github.com' % self._token.value, 1)

        return self.data['clone_url'].replace(
            url, self._token.value + '@' + url, 1)

    def get_labels(self):
        """
        Retrieves the labels of the repository.

        >>> from os import environ
        >>> repo = GitHubRepository(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test')
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
        >>> repo = GitHubRepository(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test')
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
            {'name': name, 'color': color.lstrip('#')}
        )

    def delete_label(self, name: str):
        """
        Deletes a label.

        Take a given repository:

        >>> from os import environ
        >>> repo = GitHubRepository(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test')
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

        delete(self._token, self._url + '/labels/' + name)

    def get_issue(self, issue_number: int):
        """
        Retrieves an issue:

        >>> from os import environ
        >>> repo = GitHubRepository(GitHubToken(environ['GITHUB_TEST_TOKEN']),
        ...                         'gitmate-test-user/test')
        >>> repo.get_issue(1).title
        'test issue'

        :param issue_number: The issue ID of the issue to retrieve.
        :return: An Issue object.
        :raises ElementDoesntExistError: If the issue doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        return GitHubIssue(self._token, self.full_name, issue_number)

    def get_mr(self, mr_number: int):
        """
        Retrieves an MR:

        :param mr_number: The merge_request ID of the MR to retrieve.
        :return: A MergeRequest object.
        :raises ElementDoesntExistError: If the MR doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
        return GitHubMergeRequest(self._token, self.full_name, mr_number)

    @property
    def hooks(self):
        """
        Retrieves all URLs this repository is hooked to.

        :return: Set of URLs (str).
        """
        hook_url = self._url + '/hooks'
        hooks = get(self._token, hook_url)

        # Use get since some hooks might not have a config - stupid github
        results = {hook['config'].get('url') for hook in hooks}
        results.discard(None)

        return results

    def register_hook(self,
                      url: str,
                      secret: Optional[str]=None,
                      events: Optional[Set[WebhookEvents]]=None):
        """
        Registers a webhook to the given URL. Use it as simple as:

        >>> from os import environ
        >>> repo = GitHubRepository(environ['GITHUB_TEST_TOKEN'],
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
            An optional secret token to be registered with the webhook. An
        `X-Hub-Signature` value, in the response header, computed as a HMAC
        hex digest of the body, using the `secret` as the key would be
        returned when the webhook is fired.
        :param events:
            The events for which the webhook is to be registered against.
            Defaults to all possible events.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        if url in self.hooks:
            return

        config = {'url': url, 'content_type': 'json'}
        reg_events = []

        if secret:
            config['secret'] = secret

        if events:
            reg_events = [GH_WEBHOOK_TRANSLATION[event] for event in events]

        self.data = post(
            self._token,
            self._url + '/hooks',
            {'name': 'web', 'active': True, 'config': config,
             'events': reg_events if len(reg_events) else ['*']}
        )

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
            if hook['config'].get('url', None) == url:
                delete(self._token, hook_url + '/' + str(hook['id']))

    @property
    def merge_requests(self) -> set:
        """
        Retrieves a set of merge request objects.

        >>> from os import environ
        >>> repo = GitHubRepository(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> len(repo.merge_requests)
        3
        """
        from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
        return {GitHubMergeRequest(self._token, self.full_name, res['number'])
                for res in get(self._token, self._url + '/pulls')}

    def filter_issues(self, state: str='opened') -> set:
        """
        Filters the issues from the repository based on properties.

        :param state: 'opened' or 'closed' or 'all'.
        """
        params = {'state': GH_ISSUE_STATE_TRANSLATION[state]}
        return {GitHubIssue.from_data(res, self._token,
                                      self.full_name, res['number'])
                for res in get(self._token, self._url + '/issues', params)
                if 'pull_request' not in res}

    @property
    def issues(self) -> set:
        """
        Retrieves a set of issue objects.

        >>> from os import environ
        >>> repo = GitHubRepository(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> len(repo.issues)
        81
        """
        return self.filter_issues()

    def create_issue(self, title: str, body: str='') -> GitHubIssue:
        """
        Create a new issue in the repository.

        >>> from os import environ
        >>> repo = GitHubRepository(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> iss = repo.create_issue('test issue title', 'test body title')
        >>> isinstance(iss, GitHubIssue)
        True
        """
        return GitHubIssue.create(self._token, self.full_name, title, body)

    def create_fork(self, organization: Optional[str]=None,
                    namespace: Optional[str]=None):
        """
        Creates a fork of repository.
        """
        url = self._url + '/forks'
        data = {
            'organization': organization
        }
        data = eliminate_none(data)
        response = post(self._token, url, data=data)

        return GitHubRepository(self._token, response['full_name'])

    def delete(self):
        """
        Deletes the repository
        """
        delete(self._token, self._url)

    def create_merge_request(self, title:str, base:str, head:str,
                             body: Optional[str]=None,
                             target_project_id: Optional[int]=None,
                             target_project: Optional[str]= None):
        """
        Creates a merge request to that repository
        """
        data = {'title': title, 'body': body, 'base': base,
                'head': head}
        url = self._url + '/pulls'
        json = post(self._token, url, data=data)

        from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
        return GitHubMergeRequest(self._token,
                                  json['base']['repo']['full_name'],
                                  json['number'])

    def create_file(self, path: str, message: str, content: str,
                    branch: Optional[str]=None, committer: Optional[str]=None,
                    author: Optional[dict]=None, encoding: Optional[str]=None):
        """
        Creates a new file in the Repository
        """
        url = self._url + '/contents/' + path
        content = b64encode(content.encode()).decode('utf-8')
        data = {
            'path': path,
            'message': message,
            'content': content,
            'branch': branch,
            'sha': branch,
        }
        json = put(self._token, url, data)

        from IGitt.GitHub.GitHubContent import GitHubContent
        return GitHubContent(self._token,
                             self.full_name,
                             json['content']['path'])

    def _search_in_range(
            self,
            issue_type,
            created_after: Optional[datetime]=None,
            created_before: Optional[datetime]=None,
            updated_after: Optional[datetime]=None,
            updated_before: Optional[datetime]=None,
            state: Union[MergeRequestStates, IssueStates, None]=None
    ):
        """
        Search for issue based on type 'issue' or 'pr' and return a
        list of issues.
        """
        from IGitt.GitHub.GitHub import GitHub
        if state is None:
            query = ' type:' + issue_type + ' repo:' + self.full_name
        else:
            query = (' type:' + issue_type + ' is:' + state.value +
                     ' repo:' + self.full_name)

        if ((created_after and created_before) or
                (updated_after and updated_before)):
            raise RuntimeError(('Cannot process before '
                                'and after date simultaneously'))
        if created_after:
            query += (' created:>=' +
                      str(created_after.strftime('%Y-%m-%dT%H:%M:%SZ')))
        elif created_before:
            query += (' created:<' +
                      str(created_before.strftime('%Y-%m-%dT%H:%M:%SZ')))
        if updated_after:
            query += (' updated:>=' +
                      str(updated_after.strftime('%Y-%m-%dT%H:%M:%SZ')))
        elif updated_before:
            query += (' updated:<' +
                      str(updated_before.strftime('%Y-%m-%dT%H:%M:%SZ')))
        return list(GitHub.raw_search(self._token, query))

    def search_mrs(self,
                   created_after: Optional[datetime]=None,
                   created_before: Optional[datetime]=None,
                   updated_after: Optional[datetime]=None,
                   updated_before: Optional[datetime]=None,
                   state: Optional[MergeRequestStates]=None):
        """
        List open pull request in the repository.
        """
        return self._search_in_range('pr',
                                     created_after,
                                     created_before,
                                     updated_after,
                                     updated_before,
                                     state)
    def search_issues(self,
                      created_after: Optional[datetime]=None,
                      created_before: Optional[datetime]=None,
                      updated_after: Optional[datetime]=None,
                      updated_before: Optional[datetime]=None,
                      state: Optional[IssueStates] = None):
        """
        List open issues in the repository.
        """
        return self._search_in_range('issue',
                                     created_after,
                                     created_before,
                                     updated_after,
                                     updated_before,
                                     state)

    def get_permission_level(self, user) -> AccessLevel:
        """
        Retrieves the permission level for the specified user on this
        repository.

        Note that this request can be made only if the access token used here
        has atleast write access to the repository. If not, a HTTP 403 occurs.
        """
        url = self._url + '/collaborators/{}/permission'.format(user.username)
        data = get(self._token, url)
        return {
            'admin': AccessLevel.ADMIN,
            'write': AccessLevel.CAN_WRITE,
            'read': AccessLevel.CAN_READ,
            'none': AccessLevel.NONE,
        }.get(data['permission'])
