"""
Contains the git Hoster abstraction.
"""
from typing import Iterator, Set, Union

from IGitt.Interfaces import IGittObject, Token
from IGitt.Interfaces.Repository import Repository
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.MergeRequest import MergeRequest


class Hoster(IGittObject):
    """
    Abstracts a service like GitHub and allows e.g. to query for available
    repositories and stuff like that.
    """
    @staticmethod
    def get_repo_name(webhook) -> str:
        """
        Retrieves repository name from given webhook data.
        """
        raise NotImplementedError

    @property
    def master_repositories(self) -> Set[Repository]:
        """
        Retrieves the repositories the user has administrative access to.
        """
        raise NotImplementedError

    @property
    def owned_repositories(self) -> Set[Repository]:
        """
        Retrieves the full names of the owned repositories as strings.

        :return: A set of strings.
        """
        raise NotImplementedError

    @property
    def write_repositories(self) -> Set[Repository]:
        """
        Retrieves the full names of repositories this user can write to.

        :return: A set of strings.
        """
        raise NotImplementedError

    def get_repo(self, repository) -> Repository:
        """
        Return a repository object.
        """
        raise NotImplementedError

    def handle_webhook(self, event: str, data: dict):
        """
        Handles a webhook for you.

        If it's an issue event it returns e.g.
        ``IssueActions.OPENED, [Issue(...)]``, for comments it returns
        ``MergeRequestActions.COMMENTED,
        [MergeRequest(...), Comment(...)]``.

        :param event:       The HTTP_X_GITLAB_EVENT of the request header.
        :param data:        The pythonified JSON data of the request.
        :return:            An IssueActions or MergeRequestActions member and a
                            list of the affected IGitt objects.
        """
        raise NotImplementedError

    @staticmethod
    def raw_search(token: Token, raw_query: str) -> Iterator[Union[Issue,
                                                                   MergeRequest]
                                                            ]:
        """
        Search issues using the raw_query string.

        :param token:       Token object.
        :param raw_query:   Raw query string.
        :return:            An iterator to iterator over the search results.
        """
        raise NotImplementedError
