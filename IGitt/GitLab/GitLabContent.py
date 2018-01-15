"""
This contains the Content implementation for GitLab.
"""
from typing import Optional
from typing import Union
from urllib.parse import quote_plus

from IGitt.GitLab import GitLabMixin
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab import GitLabPrivateToken
from IGitt.GitLab import delete
from IGitt.GitLab import get
from IGitt.GitLab import put
from IGitt.Interfaces.Content import Content


class GitLabContent(GitLabMixin, Content):
    """
    This class represents a content on GitHub
    """
    def __init__(self,  token: Union[GitLabOAuthToken, GitLabPrivateToken],
                 repository: str, path: str):
        self._token = token
        self._repository = repository
        self._url = ('/projects/' + quote_plus(repository) +
                     '/repository/files/' + path)

    def get_content(self, ref='master'):
        data = {
            'path': self._url,
            'ref': ref
        }
        self.data = get(token=self._token, url=self._url, params=data)

    def delete(self, message: str, branch: Optional[str]=None):
        """
        Deletes content

        :param message: The commit message for the deletion commit.
        :param branch:  The branch to delete this content from. Defaults to
                        `master`.
        """
        if branch is None:
            branch = 'master'

        data = {
            'file_path': self._url,
            'branch': branch,
            'commit_message': message
        }
        delete(self._token, url=self._url, params=data)

    def update(self, message: str, content: str, branch: Optional[str]=None):

        if branch is None:
            branch = 'master'

        data = {
            'file_path': self._url,
            'commit_message': message,
            'branch': branch,
            'content' : content
        }
        put(token=self._token, url=self._url, data=data)
