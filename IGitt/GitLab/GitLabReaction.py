"""
Contains an object representation of a reaction / award emoji on GitLab.
"""
from typing import Union

from IGitt.GitLab import GitLabMixin
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab import GitLabPrivateToken
from IGitt.GitLab.GitLabUser import GitLabUser
from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.Reaction import Reaction


class GitLabReaction(GitLabMixin, Reaction):
    """
    A GitLab Reaction or Award Emoji, e.g. heart.
    """
    def __init__(self,
                 token: Union[GitLabOAuthToken, GitLabPrivateToken],
                 related: Union[Issue, MergeRequest, Comment],
                 identifier: int):
        """
        Creates a GitLabReaction instance.

        :param token:       The authentication token.
        :param token:       The authentication token.
        :param related:     The object this reaction was added on,
                            i.e. an Issue, MergeRequest, Comment, etc.
        :param identifier:  The unique identifier of the reaction.
        """
        self._token = token
        self._related = related
        self._url = '{}/award_emoji/{}'.format(
            getattr(related, '_url'), identifier)
        self._identifier = identifier

    @property
    def name(self) -> str:
        """
        Retrieves the name of the reaction.
        """
        return self.data['name']

    @property
    def user(self) -> GitLabUser:
        """
        Retrieves the user who reacted with this reaction.
        """
        user = self.data['user']
        return GitLabUser.from_data(user, self._token, user['id'])
