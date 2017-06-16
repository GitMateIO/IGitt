"""
Contains the GitLab Repository implementation.
"""
from urllib.parse import quote_plus

from IGitt import ElementAlreadyExistsError, ElementDoesntExistError
from IGitt.GitLab import delete, get, post, GitLabMixin
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.Interfaces.Repository import Repository


class GitLabRepository(Repository, GitLabMixin):
    """
    Represents a repository on GitLab.
    """

    def __init__(self, oauth_token: str, repository: str):
        """
        Creates a new GitLabRepository object with the given credentials.

        :param oauth_token: The OAuth token.
        :param repository: The full name of the repository,
                           e.g. ``sils/baritone``.
        """
        self._token = oauth_token
        self._repository = repository
        self._url = '/projects/' + quote_plus(repository)

    @property
    def hoster(self) -> str:
        """
        Indicates that the repository is hosted by GitLab.

        :return: "gitlab".
        """
        return 'gitlab'  # dont cover

    @property
    def full_name(self) -> str:
        """
        Retrieves the full name of the repository, e.g. "sils/baritone".

        >>> from os import environ
        >>> repo = GitLabRepository(environ['GITLAB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> repo.full_name
        'gitmate-test-user/test'

        :return: The full repository name as string.
        """
        return self._repository

    @property
    def clone_url(self) -> str:
        """
        Retrieves the URL of the repository.

        >>> from os import environ as env
        >>> repo = GitLabRepository(env['GITLAB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> expected = 'https://{}@gitlab.com/gitmate-test-user/test.git'
        >>> assert repo.clone_url == expected.format(env['GITLAB_TEST_TOKEN'])

        :return: A URL that can be used to clone the repository with Git.
        """
        return self.data['http_url_to_repo'].replace(
            'gitlab.com', 'oauth2:' + self._token + '@gitlab.com', 1)

    def get_labels(self) -> {str}:
        """
        Retrieves the labels of the repository.

        >>> from os import environ
        >>> repo = GitLabRepository(environ['GITLAB_TEST_TOKEN'],
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
        >>> repo = GitLabRepository(environ['GITLAB_TEST_TOKEN'],
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
            {'name': name, 'color': color}
        )

    def delete_label(self, name: str):
        """
        Deletes a label.

        Take a given repository:

        >>> from os import environ
        >>> repo = GitLabRepository(environ['GITLAB_TEST_TOKEN'],
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

        delete(self._token, self._url + '/labels', {'name': name})

    def get_issue(self, issue_number: int) -> GitLabIssue:
        """
        Retrieves an issue:

        >>> from os import environ
        >>> repo = GitLabRepository(environ['GITLAB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
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
    def hooks(self) -> {str}:
        """
        Retrieves all URLs this repository is hooked to.

        :return: Set of URLs (str).
        """
        hook_url = self._url + '/hooks'
        hooks = get(self._token, hook_url)

        return {hook['url'] for hook in hooks}

    def register_hook(self, url: str, secret: str=None):
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
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        if url in self.hooks:
            return

        config = {
            'url': url,
            'push_events': True,
            'issues_events': True,
            'merge_requests_events': True,
            'tag_push_events': True,
            'note_events': True,
            'job_events': True,
            'pipeline_events': True,
            'wiki_events': True,
            'enable_ssl_verification': False,
        }

        if secret is not None:
            config['token'] = secret

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
        >>> repo = GitLabRepository(environ['GITLAB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> len(repo.merge_requests)
        4
        """
        from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
        return {GitLabMergeRequest(self._token, self.full_name, res['iid'])
                for res in get(self._token, self._url + '/merge_requests')}
