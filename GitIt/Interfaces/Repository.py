"""
Contains the Repository base class.
"""

from tempfile import mkdtemp

from git.repo.base import Repo


class Repository:
    """
    This class depicts a Repository at a hosting service like GitHub. Thus, on
    top of access to the actual code and history, it also provides access to
    issues, PRs, hooks and so on.
    """

    def register_hook(self, url: str):
        """
        Registers a webhook to the given URL.

        :param url: The URL to fire the webhook to.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def get_commit(self, sha: str):
        """
        Retrieves the commit with the given SHA.

        :return: A commit object.
        :raises ElementDoesntExistError: If the commit doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def get_pull_request(self, pr_number: int):
        """
        Retrieves the PR with the associated ID.

        :param pr_number: The ID of the PR to retrieve.
        :return: A PullRequest object.
        :raises ElementDoesntExistError: If the PR doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def get_issue(self, issue_number: int):
        """
        Retrieves an issue.

        :param issue_number: The issue ID of the issue to retrieve.
        :return: An Issue object.
        :raises ElementDoesntExistError: If the issue doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def create_label(self, name: str, color: str):
        """
        Creates a new label.

        :param name: The name of the label to create.
        :param color: A HTML color value with a leading #.
        :raises ElementAlreadyExistsError: If the label name already exists.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def get_clone(self) -> (Repo, str):
        """
        Clones the repository into a temporary directory:

        >>> test_repo = type(
        ...     'MockRepo', (Repository,),
        ...     {'clone_url': 'https://github.com/sils1297/configurations'})
        >>> repo, path = test_repo().get_clone()

        With this Repo object you can easily access the source code of the
        repository as well as all commits:

        >>> type(repo)
        <class 'git.repo.base.Repo'>
        >>> repo.branches
        [<git.Head "refs/heads/master">]

        Or simply access it via the path if you care only for the head:

        >>> from os.path import exists, join
        >>> assert exists(join(path, '.gitignore'))

        Be sure to not forget to clean it up in the end:

        >>> from shutil import rmtree
        >>> rmtree(path)

        :return: A tuple containing a Repo object and the path to the
                 repository.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        tempdir = mkdtemp()
        repo = Repo.clone_from(self.clone_url, tempdir)

        return repo, tempdir

    def get_labels(self) -> {str}:
        """
        Retrieves the set of labels.

        :return: A set of strings, the captions of the labels.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def hoster(self) -> str:
        """
        Retrieves the name of the hoster.

        :return: A string, e.g. 'github' or 'gitlab'.
        """
        raise NotImplementedError

    @property
    def full_name(self) -> str:
        """
        Retrieves the full name of the repository, that identifies it uniquely
        at the hoster.

        :return: A string, e.g. 'coala-analyzer/coala'.
        """
        raise NotImplementedError

    @property
    def access_key(self) -> str:
        """
        Retrieves the access key.

        :return: A string, usually an OAuth token.
        """
        raise NotImplementedError

    @property
    def clone_url(self) -> str:
        """
        Retrieves an url that can be used for cloning the repository.

        :return: A string that can be used with ``git clone <url>`` as url.
        """
        raise NotImplementedError
