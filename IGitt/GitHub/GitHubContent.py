"""
This contains the Content implementation for GitHub.
"""
from IGitt.GitHub import GitHubMixin, GitHubToken
from IGitt.Interfaces.Content import Content


class GitHubContent(Content, GitHubMixin):
    """
    This class represents a content on GitHub
    """
    def __init__(self,  token: GitHubToken, repository: str, path: str):
        self._token = token
        self._repository = repository
        self._url = '/repos' + repository + '/contents/' + path
