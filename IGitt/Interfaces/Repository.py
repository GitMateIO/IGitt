"""
Contains the Repository class.
"""

from datetime import datetime
from enum import Enum
from os import chdir, getcwd
from tempfile import mkdtemp
from typing import Optional
from typing import Set
from typing import Union

from git.repo.base import Repo

from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces import IGittObject
from IGitt.Interfaces import MergeRequestStates
from IGitt.Interfaces import IssueStates


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


class Repository(IGittObject):
    """
    This class depicts a Repository at a hosting service like GitHub. Thus, on
    top of access to the actual code and history, it also provides access to
    issues, PRs, hooks and so on.
    """

    @property
    def identifier(self) -> int:
        """
        Returns the identifier of the repository.
        """
        raise NotImplementedError

    @property
    def top_level_org(self):
        """
        Returns the topmost organization, e.g. for `gitmate/open-source/IGitt`
        this is `gitmate`.
        """
        raise NotImplementedError

    def register_hook(self,
                      url: str,
                      secret: Optional[str]=None,
                      events: Optional[Set[WebhookEvents]]=None):
        """
        Registers a webhook to the given URL. Should pass silently if the hook
        already exists.

        :param url: The URL to fire the webhook to.
        :param secret: An optional secret token to be registered with webhook.
        :param events: The set of events for which the webhook is to be
                       registered against. Defaults to all possible events.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def delete_hook(self, url: str):
        """
        Deletes all webhooks to the given URL. (Does nothing if no such hook
        exists.)

        :param url: The URL to not fire the webhook to anymore.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def hooks(self) -> Set[str]:
        """
        Retrieves all URLs this repository is hooked to.

        :return: Set of URLs (str).
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

    def get_mr(self, mr_number: int):
        """
        Retrieves an MR.

        :param mr_number: The merge_request ID of the MR to retrieve.
        :return: An MR object.
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

    def delete_label(self, name: str):
        """
        Deletes a label.

        :param name: The caption of the label to delete.
        :raises ElementDoesntExistError: If the label doesn't exist.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def get_clone(self) -> Union[Repo, str]:
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

        # Workaround for
        # https://github.com/gitpython-developers/GitPython/issues/734
        try:
            getcwd()
        except FileNotFoundError:
            chdir(tempdir)

        repo = Repo.clone_from(self.clone_url, tempdir)

        return repo, tempdir

    def get_labels(self) -> Set[str]:
        """
        Retrieves the set of labels.

        :return: A set of strings, the captions of the labels.
        :raises RuntimeError: If something goes wrong (network, auth...).
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
    def commits(self):
        """
        Retrieves the set of commits in this repository.

        :return: Set of Commit objects.
        """
        raise NotImplementedError

    @property
    def clone_url(self) -> str:
        """
        Retrieves an url that can be used for cloning the repository.

        :return: A string that can be used with ``git clone <url>`` as url.
        """
        raise NotImplementedError

    @property
    def merge_requests(self) -> set:
        """
        Retrieves a set of merge request objects.
        """
        raise NotImplementedError

    def filter_issues(self, state: str='opened') -> set:
        """
        Filters the issues from the repository based on properties.

        :param state: 'opened' or 'closed' or 'all'.
        """
        raise NotImplementedError

    @property
    def issues(self) -> set:
        """
        Retrieves a set of issue objects.
        """
        raise NotImplementedError

    def create_issue(self, title, body=''):
        """
        Create a new issue.
        """
        raise NotImplementedError

    def create_fork(self, organization: Optional[str]=None,
                    namespace: Optional[str]=None):
        """
        Create a fork
        """
        raise NotImplementedError

    def delete(self):
        """
        Delete Repository
        """
        raise NotImplementedError

    def create_merge_request(self, title: str, base: str, head: str,
                             body: Optional[str]=None,
                             target_project_id: Optional[int]=None,
                             target_project: Optional[str]=None):
        """
        Creates a PR
        """
        raise NotImplementedError

    def create_file(self, path: str, message: str, content: str,
                    branch: Optional[str]=None, committer: Optional[str]=None,
                    author: Optional[dict]=None, encoding: Optional[str]=None):
        """
        Creates a new file
        """
        raise NotImplementedError

    def search_mrs(self,
                   created_after: Optional[datetime]=None,
                   created_before: Optional[datetime]=None,
                   updated_after: Optional[datetime]=None,
                   updated_before: Optional[datetime]=None,
                   state: Optional[MergeRequestStates]=None):
        """
        Retrieves a list of prs
        """
        raise NotImplementedError

    def search_issues(self,
                      created_after: Optional[datetime]=None,
                      created_before: Optional[datetime]=None,
                      updated_after: Optional[datetime]=None,
                      updated_before: Optional[datetime]=None,
                      state: Optional[IssueStates]=None):
        """
        Retrieves a list of issues
        """
        raise NotImplementedError

    def get_permission_level(self, user) -> AccessLevel:
        """
        Retrieves the permission level for the specified user on this
        repository.
        """
        raise NotImplementedError
