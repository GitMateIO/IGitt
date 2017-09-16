"""
Contains the Repository class.
"""
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty
from datetime import datetime
from enum import Enum
from tempfile import mkdtemp

from git.repo.base import Repo


class WebhookEvents(Enum):
    """
    This class depicts the webhook events that can be registered with any
    hosting service providers like GitHub or GitLab.
    """
    PUSH = 1
    ISSUE = 2
    MERGE_REQUEST = 3
    ISSUE_COMMENT = 4
    COMMIT_COMMENT = 5
    MERGE_REQUEST_COMMENT = 6


class Repository(metaclass=ABCMeta):
    """
    This class depicts a Repository at a hosting service like GitHub. Thus, on
    top of access to the actual code and history, it also provides access to
    issues, PRs, hooks and so on.
    """

    @abstractmethod
    def register_hook(self,
                      url: str,
                      secret: str=None,
                      events: {WebhookEvents}=None):
        """
        Registers a webhook to the given URL. Should pass silently if the hook
        already exists.

        :param url: The URL to fire the webhook to.
        :param secret: An optional secret token to be registered with webhook.
        :param events: The set of events for which the webhook is to be
                       registered against. Defaults to all possible events.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """

    @abstractmethod
    def delete_hook(self, url: str):
        """
        Deletes all webhooks to the given URL. (Does nothing if no such hook
        exists.)

        :param url: The URL to not fire the webhook to anymore.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """

    @abstractproperty
    def hooks(self) -> {str}:
        """
        Retrieves all URLs this repository is hooked to.

        :return: Set of URLs (str).
        """

    @abstractmethod
    def get_issue(self, issue_number: int):
        """
        Retrieves an issue.

        :param issue_number: The issue ID of the issue to retrieve.
        :return: An Issue object.
        :raises ElementDoesntExistError: If the issue doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """

    @abstractmethod
    def get_mr(self, mr_number: int):
        """
        Retrieves an MR.

        :param mr_number: The merge_request ID of the MR to retrieve.
        :return: An MR object.
        """

    @abstractmethod
    def create_label(self, name: str, color: str):
        """
        Creates a new label.

        :param name: The name of the label to create.
        :param color: A HTML color value with a leading #.
        :raises ElementAlreadyExistsError: If the label name already exists.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """

    @abstractmethod
    def delete_label(self, name: str):
        """
        Deletes a label.

        :param name: The caption of the label to delete.
        :raises ElementDoesntExistError: If the label doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """

    def get_clone(self) -> (Repo, str):
        """
        Clones the repository into a temporary directory:

        >>> test_repo = type(
        ...     'MockRepo', (Repository,),
        ...     {'clone_url': 'https://github.com/sils/configurations'})
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

    @abstractmethod
    def get_labels(self) -> {str}:
        """
        Retrieves the set of labels.

        :return: A set of strings, the captions of the labels.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """

    @abstractproperty
    def hoster(self) -> str:
        """
        Retrieves the name of the hoster.

        :return: A string, e.g. 'github' or 'gitlab'.
        """

    @abstractproperty
    def full_name(self) -> str:
        """
        Retrieves the full name of the repository, that identifies it uniquely
        at the hoster.

        :return: A string, e.g. 'coala-analyzer/coala'.
        """

    @abstractproperty
    def clone_url(self) -> str:
        """
        Retrieves an url that can be used for cloning the repository.

        :return: A string that can be used with ``git clone <url>`` as url.
        """

    @abstractproperty
    def merge_requests(self) -> set:
        """
        Retrieves a set of merge request objects.
        """

    @abstractmethod
    def filter_issues(self, state: str='opened') -> set:
        """
        Filters the issues from the repository based on properties.

        :param state: 'opened' or 'closed' or 'all'.
        """

    @abstractproperty
    def issues(self) -> set:
        """
        Retrieves a set of issue objects.
        """

    @abstractmethod
    def create_issue(self, title, body=''):
        """
        Create a new issue.
        """

    @abstractmethod
    def create_fork(self, organization: (str, None)=None,
                    namespace: (str, None)=None):
        """
        Create a fork
        """

    @abstractmethod
    def delete(self):
        """
        Delete Repository
        """

    @abstractmethod
    def create_merge_request(self, title:str, base:str, head:str,
                             body: (str, None)=None,
                             target_project_id: (int, None)=None,
                             target_project: (str, None) = None):
        """
        Creates a PR
        """

    @abstractmethod
    def create_file(self, path: str, message: str, content: str,
                    branch: (str, None)=None, committer:(str, None)=None,
                    author:(dict, None)=None, encoding: (str, None)=None,):
        """
        Creates a new file
        """

    @abstractmethod
    def search_mrs(self,
                   created_after: datetime.date='',
                   created_before: datetime.date='',
                   updated_after: datetime.date='',
                   updated_before: datetime.date=''):
        """
        Retrieves a list of open prs
        """
        raise NotImplementedError

    @abstractmethod
    def search_issues(self,
                      created_after: datetime.date='',
                      created_before: datetime.date='',
                      updated_after: datetime.date='',
                      updated_before: datetime.date=''):
        """
        Retrieves a list of open issues
        """
        raise NotImplementedError
