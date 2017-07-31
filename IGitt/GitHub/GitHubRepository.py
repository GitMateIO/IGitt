"""
Contains the GitHub Repository implementation.
"""
from datetime import datetime

from IGitt import ElementAlreadyExistsError, ElementDoesntExistError
from IGitt.GitHub import delete, get, post, GitHubMixin, put
from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.Interfaces.Repository import Repository
from IGitt.Interfaces.Repository import WebhookEvents
from IGitt.Utils import eliminate_none
from base64 import b64encode

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


class GitHubRepository(Repository, GitHubMixin):
    """
    Represents a repository on GitHub.
    """



    def __init__(self, token: GitHubToken, repository: str):
        """
        Creates a new GitHubRepository object with the given credentials.

        :param token: A GitHubToken object to authenticate with.
        :param repository: The full name of the repository,
                           e.g. ``sils/something``.
        """
        self._token = token
        self._repository = repository
        self._url = '/repos/'+repository

    @property
    def hoster(self):
        """
        Indicates that the repository is hosted by GitHub.

        :return: "github".
        """
        return "github"  # dont cover

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
        return self._repository

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
        return self.data['clone_url'].replace(
            'github.com', self._token.value + '@github.com', 1)

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
            raise ElementAlreadyExistsError(name + " already exists.")

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
            raise ElementDoesntExistError(name + " doesnt exist.")

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
                      secret: str=None,
                      events: {WebhookEvents}=None):
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
        return {GitHubIssue(self._token, self.full_name, res['number'])
                for res in get(self._token, self._url + '/issues', params)}

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

    def create_fork(self, organization: (str, None)=None,
                    namespace: (str, None)=None):
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
                             body: (str, None)=None,
                             target_project_id: (int, None)=None,
                             target_project: (str, None) = None):
        """
        Creates a merge request to that repository
        """
        data = {'title': title, 'body': body, 'base': base,
                'head': head}
        url = self._url + '/pulls'
        json = post(self._token, url, data=data)

        from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
        return GitHubMergeRequest(self._token, json['base']['repo']['full_name'], json['number'])

    def create_file(self, path: str, message: str, content: str,
                    branch: (str, None)=None, committer:(str, None)=None,
                    author:(dict, None)=None, encoding:(str, None)=None):
        """
        Creates a new file in the Repository
        """
        url = self._url + '/contents/' + path
        content = b64encode(content.encode()).decode('utf-8')
        data = { 'path' : path,
                 'message': message, 'content': content, 'branch': branch}
        json = put(self._token, url, data)

        from IGitt.GitHub.GitHubContent import GitHubContent
        return GitHubContent(self._token, self._repository, json['content']['path'])

    def _search(self,
                issue_type,
                created_after: datetime.date='',
                created_before: datetime.date='',
                updated_after: datetime.date='',
                updated_before: datetime.date=''):
        """
        Search for issue based on type 'issue' or 'pr' and return a
        list of issues.
        """
        query = ' type:' + issue_type + ' state:open repo:' + self._repository
        if ((created_after and created_before)
                or (updated_after and updated_before)):
            raise RuntimeError(('Cannot process before '
                                'and after date simultaneously'))
        if created_after:
            query += ' created:>=' + str(created_after)
        elif created_before:
            query += ' created:<' + str(created_before)
        if updated_after:
            query += ' updated:>=' + str(updated_after)
        elif updated_before:
            query += ' updated:<' + str(updated_before)
        base_url = '/search/issues'
        query_params = {'q': query,
                        'per_page': '100'}
        resp = get(self._token, base_url, query_params)
        return resp

    def search_mrs(self,
                   created_after: datetime.date='',
                   created_before: datetime.date='',
                   updated_after: datetime.date='',
                   updated_before: datetime.date=''):
        """
        List open pull request in the repository.
        """
        for pr_data in self._search('pr',
                                    created_after,
                                    created_before,
                                    updated_after,
                                    updated_before):
            pull_request = self.get_mr(pr_data['number'])
            pull_request.data = pr_data
            yield pull_request

    def search_issues(self,
                      created_after: datetime.date='',
                      created_before: datetime.date='',
                      updated_after: datetime.date='',
                      updated_before: datetime.date=''):
        """
        List open issues in the repository.
        """
        for issue_data in self._search('issue',
                                       created_after,
                                       created_before,
                                       updated_after,
                                       updated_before):
            issue = self.get_issue(issue_data['number'])
            issue.data = issue_data
            yield issue
