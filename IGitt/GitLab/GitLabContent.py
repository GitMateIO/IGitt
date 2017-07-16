"""
This contains the Content implementation for GitLab.
"""
from urllib.parse import quote_plus

from IGitt.GitLab import GitLabMixin, GitLabOAuthToken, GitLabPrivateToken
from IGitt.Interfaces.Content import Content


class GitLabContent(Content, GitLabMixin):
    """
    This class represents a content on GitHub
    """
    def __init__(self,  token: (GitLabOAuthToken, GitLabPrivateToken),
                 repository: str, path: str):
        self._token = token
        self._repository = repository
        self._url = '/projects/' + quote_plus(repository) + '/repository/files/' + path
