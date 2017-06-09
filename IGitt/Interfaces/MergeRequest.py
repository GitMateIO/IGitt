"""
Contains a class that represents a request to merge something into some git
branch.
"""
from datetime import datetime

from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.Issue import Issue


class MergeRequest(Issue):
    """
    A request to merge something into the main codebase. Can be a patch in a
    mail or a pull request on GitHub.
    """

    def close(self):
        """
        Closes the merge request.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def reopen(self):
        """
        Reopens the merge request.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def state(self) -> str:
        """
        Get's the state of the merge request.

        :return: Either 'open' or 'closed'.
        """
        raise NotImplementedError

    @property
    def base(self) -> Commit:
        """
        Retrieves the base commit of the merge request, i.e. the one it should
        be merged into.

        :return: A Commit object.
        """
        raise NotImplementedError

    @property
    def base_branch_name(self) -> str:
        """
        Retrieves the base branch name of the merge request, i.e. the one it
        should be merged into.

        :return: A string.
        """
        raise NotImplementedError

    @property
    def head(self) -> Commit:
        """
        Retrieves the head commit of the merge request, i.e. the one which
        would be merged.

        :return: A Commit object.
        """
        raise NotImplementedError

    @property
    def head_branch_name(self) -> str:
        """
        Retrieves the head branch name of the merge request, i.e. the one that
        will be merged.

        :return: A string.
        """
        raise NotImplementedError

    @property
    def commits(self) -> [Commit]:
        """
        Retrieves all commits that are contained in this request.

        :return: A list of Commits.
        """
        raise NotImplementedError

    @property
    def repository(self):
        """
        Retrieves the repository where this PR is from.

        :return: A Repository object.
        """
        raise NotImplementedError

    @property
    def affected_files(self):
        """
        Retrieves the affected files.

        :return: A set of filenames relative to repo root.
        """
        raise NotImplementedError

    @property
    def diffstat(self):
        """
        Gets additions and deletions of a merge request.

        :return: An (additions, deletions) tuple.
        """
        raise NotImplementedError

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the merge request was created.
        """
        raise NotImplementedError

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the merge request was updated the last
        time.
        """
        raise NotImplementedError

    @property
    def number(self) -> int:
        """
        Returns the MR "number" or id.
        """
        raise NotImplementedError
