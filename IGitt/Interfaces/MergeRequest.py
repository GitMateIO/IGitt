"""
Contains a class that represents a request to merge something into some git
branch.
"""

from IGitt.Interfaces.Commit import Commit


class MergeRequest:
    """
    A request to merge something into the main codebase. Can be a patch in a
    mail or a pull request on GitHub.
    """

    @property
    def base(self) -> Commit:
        """
        Retrieves the base commit of the merge request, i.e. the one it should
        be merged into.

        :return: A Commit object.
        """
        raise NotImplementedError

    @property
    def head(self) -> Commit:
        """
        Retrieves the head commit of the merge request, i.e. the one that
        will be merged.

        :return: A Commit object.
        """
        raise NotImplementedError

    @property
    def commits(self) -> [Commit]:
        """
        Retrieves all commits that are contained in this request.

        :return: A list of Commits.
        """
        raise NotImplementedError
