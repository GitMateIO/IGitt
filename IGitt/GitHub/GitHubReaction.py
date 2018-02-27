"""
Contains an object representation of a reaction on GitHub.
"""
from functools import lru_cache
from typing import Union

from IGitt.GitHub import get
from IGitt.GitHub import GitHubMixin
from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces.Reaction import Reaction


PREVIEW_HEADER = {'Accept': 'application/vnd.github.squirrel-girl-preview'}


class GitHubReaction(GitHubMixin, Reaction):
    """
    A GitHub reaction, e.g. heart.
    """
    @lru_cache(None)
    def _get_data(self):
        # Note: A GitHub reaction cannot be retrieved using a GET request, it
        # has to retrieved as a list and filtered for the match.
        if not getattr(self, '_list', None):
            setattr(self, '_list', get(self._token, self._url,
                                       headers=PREVIEW_HEADER))
        try:
            return list(filter(lambda x: x['id'] == self._identifier,
                               getattr(self, '_list')))[0]
        except IndexError:
            raise RuntimeError({
                'message': 'Not Found',
                'documentation_url': 'https://developer.github.com/v3'}, 404)

    def __init__(self,
                 token: GitHubToken,
                 related: Union[Issue, MergeRequest, Comment],
                 identifier: int):
        """
        Creates a GitHubReaction instance.

        :param token:       The authentication token.
        :param related:     The object this reaction was added on,
                            i.e. an Issue, MergeRequest, Comment, etc.
        :param identifier:  The unique identifier of the reaction.
        """
        self._token = token
        self._related = related
        self._url = '{}/reactions'.format(getattr(related, '_url'))
        self._identifier = identifier

    @property
    def name(self) -> str:
        """
        Retrieves the name of the reaction.
        """
        return self.data['content']

    @property
    def user(self) -> GitHubUser:
        """
        Retrieves the user who reacted with this reaction.
        """
        user = self.data['user']
        return GitHubUser.from_data(user, self._token, user['login'])

    def __hash__(self):
        """
        Unique hash for this thing.
        """
        return hash(self.url + str(self._identifier))
