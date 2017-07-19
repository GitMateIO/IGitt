"""
This contains the Content implementation for GitLab.
"""
from urllib.parse import quote_plus

from IGitt.GitLab import GitLabMixin, GitLabOAuthToken, GitLabPrivateToken, get, delete, put
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

    def get_content(self, ref='master'):
        data = {
            'path': self._url,
            'ref': ref
        }
        self.data = get(token=self._token, url=self._url, params=data)

    def delete(self, message: str, branch: (str, None) = None):

        if branch is None:
            branch = 'master'

        data = {
            'file_path': self._url,
            'branch': branch,
            'commit_message': message
        }
        delete(self._token, url=self._url, params=data)

    def update(self, message: str, content: str, branch: (str, None) = None):

        if branch is None:
            branch = 'master'

        data = {
            'file_path': self._url,
            'commit_message': message,
            'branch': branch,
            'content' : content
        }
        put(token=self._token, url=self._url, data=data)
