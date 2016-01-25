"""
Contains a class representing the GitHub pull request.
"""
from IGitt.GitHub import query
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.Interfaces.MergeRequest import MergeRequest


class GitHubMergeRequest(MergeRequest):
    """
    A Pull Request on GitHub.
    """

    def __init__(self, oauth_token: str, repository: str, pr_number: int):
        """
        Creates a new Pull Request.

        :param oauth_token: The OAuth token to authenticate with.
        :param repository: The repository containing the PR.
        :param pr_number: The PR number.
        """
        self._token = oauth_token
        self._repository = repository
        self._number = pr_number
        self._url = '/repos/' + repository + '/pulls/' + str(pr_number)
        self._data = query(self._token, self._url)

    @property
    def base(self):
        """
        Retrieves the base commit as a commit object.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.base.sha
        '674498fd415cfadc35c5eb28b8951e800f357c6f'

        :return: A Commit object.
        """
        return GitHubCommit(self._token, self._repository,
                            self._data['base']['sha'])

    @property
    def head(self):
        """
        Retrieves the head commit as a commit objet.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> pr.head.sha
        'f6d2b7c66372236a090a2a74df2e47f42a54456b'

        :return: A Commit object.
        """
        return GitHubCommit(self._token, self._repository,
                            self._data['head']['sha'])

    @property
    def commits(self):
        """
        Retrieves a list of commit objects that are included in the PR.

        >>> from os import environ
        >>> pr = GitHubMergeRequest(environ['GITHUB_TEST_TOKEN'],
        ...                         'gitmate-test-user/test', 7)
        >>> [commit.sha for commit in pr.commits]
        ['f6d2b7c66372236a090a2a74df2e47f42a54456b']

        :return: A list of commit objects.
        """
        commits = query(self._token, self._url + '/commits')
        return [GitHubCommit(self._token, self._repository, commit['sha'])
                for commit in commits]
