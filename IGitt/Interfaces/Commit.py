"""
This module contains the actual commit object.
"""

from IGitt.Interfaces.CommitStatus import CommitStatus, Status
from IGitt.Interfaces.Repository import Repository


class Commit:
    """
    An abstraction representing a commit. This especially exposes functions to
    place comments and manipulate the status.
    """

    def ack(self):
        """
        Acknowledges the commit by setting the manual review GitMate status to
        success.

        >>> CommitMock = type('CommitMock', (Commit,),
        ...                   {'set_status': lambda self, s: print(s.status)})
        >>> CommitMock().ack()
        Status.SUCCESS

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        status = CommitStatus(Status.SUCCESS, 'This commit was acknowledged.',
                              'review/gitmate/manual', 'http://gitmate.io/')
        self.set_status(status)

    def unack(self):
        """
        Unacknowledges the commit by setting the manual review GitMate status to
        failed.

        >>> CommitMock = type('CommitMock', (Commit,),
        ...                   {'set_status': lambda self, s: print(s.status)})
        >>> CommitMock().unack()
        Status.FAILED

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        status = CommitStatus(Status.FAILED, 'This commit needs work.',
                              'review/gitmate/manual', 'http://gitmate.io/')
        self.set_status(status)

    def pending(self):
        """
        Sets the commit to a pending manual review state if there is no manual
        review state yet.

        Given a commit with an unrelated status:

        >>> CommitMock = type(
        ...     'CommitMock', (Commit,),
        ...     {'set_status': lambda self, s: self.statuses.append(s),
        ...      'get_statuses': lambda self: self.statuses,
        ...      'statuses': []})
        >>> commit = CommitMock()
        >>> commit.set_status(CommitStatus(Status.FAILED, context='unrelated'))
        >>> len(commit.get_statuses())
        1

        The invocation of pending will now add a pending status:

        >>> commit.pending()
        >>> len(commit.get_statuses())
        2
        >>> commit.get_statuses()[1].context
        'review/gitmate/manual'

        However, if there is already a manual review state, the invocation of
        pending won't affect the status:

        >>> commit.get_statuses().clear()
        >>> commit.ack()
        >>> commit.pending()  # Won't do anything
        >>> len(commit.get_statuses())
        1
        >>> commit.get_statuses()[0].status
        <Status.SUCCESS: 1>

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        for status in self.get_statuses():
            if status.context == 'review/gitmate/manual':
                return

        status = CommitStatus(Status.PENDING, 'This commit needs review.',
                              'review/gitmate/manual', 'http://gitmate.io')
        self.set_status(status)

    def comment(self, message: str, file: (str, None)=None,
                line: (int, None)=None, mr_number: int=None):
        """
        Puts a comment on the new version of the given line. If the file or
        line is None, the comment will be placed at the bottom of the commit.

        :param message:   The message to comment.
        :param file:      Filename or None
        :param line:      Line number or None
        :param mr_number: The number of a merge request if this should end up in
                          the review UI of the merge request.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def set_status(self, status: CommitStatus):
        """
        Adds the given status to the commit. If a status with the same context
        already exists, it will be bluntly overridden.

        :param status: The CommitStatus to set to this commit.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def get_statuses(self) -> {CommitStatus}:
        """
        Retrieves the all commit statuses.

        :return: A (frozen)set of CommitStatus objects.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def sha(self) -> str:
        """
        Retrieves the sha of the commit.

        :return: A string holding the SHA of the commit.
        """
        raise NotImplementedError

    @property
    def parent(self):
        """
        Retrieves the parent commit if possible.

        :return: A Commit object.
        """
        raise NotImplementedError

    @property
    def repository(self) -> Repository:
        """
        Retrieves the repository that holds this commit.

        :return: A Repository object.
        """
        raise NotImplementedError
