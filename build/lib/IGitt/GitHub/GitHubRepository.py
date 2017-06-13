"""
Contains the GitHub Repository implementation.
"""

from IGitt import ElementAlreadyExistsError, ElementDoesntExistError
from IGitt.GitHub import delete, get, post
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.Interfaces.Repository import Repository


class GitHubRepository(Repository):
    """
    Represents a repository on GitHub.
    """

    def __init__(self, oauth_token: str, repository: str):
        """
        Creates a new GitHubRepository object with the given credentials.

        :param oauth_token: The OAuth token.
        :param repository: The full name of the repository,
                           e.g. ``sils/something``.
        """
        self._token = oauth_token
        self._repository = repository
        self._url = '/repos/'+repository
        self._data = get(self._token, self._url)

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
        >>> repo = GitHubRepository(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> repo.full_name
        'gitmate-test-user/test'

        :return: The full repository name as string.
        """
        return self._data['full_name']

    @property
    def clone_url(self):
        """
        Retrieves the URL of the repository.

        >>> from os import environ as env
        >>> repo = GitHubRepository(env['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> expected = 'https://{}@github.com/gitmate-test-user/test.git'
        >>> assert repo.clone_url == expected.format(env['GITHUB_TEST_TOKEN'])

        :return: A URL that can be used to clone the repository with Git.
        """
        return self._data['clone_url'].replace(
            'github.com', self._token + '@github.com', 1)

    def get_labels(self):
        """
        Retrieves the labels of the repository.

        >>> from os import environ
        >>> repo = GitHubRepository(environ['GITHUB_TEST_TOKEN'],
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
        >>> repo = GitHubRepository(environ['GITHUB_TEST_TOKEN'],
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

        post(self._token, self._url + '/labels',
             {'name': name, 'color': color.lstrip('#')})

    def delete_label(self, name: str):
        """
        Deletes a label.

        Take a given repository:

        >>> from os import environ
        >>> repo = GitHubRepository(environ['GITHUB_TEST_TOKEN'],
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
        >>> repo = GitHubRepository(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test')
        >>> repo.get_issue(1).title
        'test issue'

        :param issue_number: The issue ID of the issue to retrieve.
        :return: An Issue object.
        :raises ElementDoesntExistError: If the issue doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        return GitHubIssue(self._token, self.full_name, issue_number)

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

    def register_hook(self, url: str, secret: str=None):
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
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        if url in self.hooks:
            return

        config = {'url': url, 'content_type': 'json'}

        if secret:
            config['secret'] = secret

        post(self._token, self._url + '/hooks',
             {'name': 'web', 'active': True, 'events': ['*'],
              'config': config})

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
