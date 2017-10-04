import os

from IGitt.Interfaces import _fetch
from IGitt.Interfaces import error_checked_request
from IGitt.GitHub import BASE_URL as GITHUB_BASE_URL
from IGitt.GitHub import GitHubToken
from IGitt.GitLab import BASE_URL as GITLAB_BASE_URL
from IGitt.GitLab import GitLabOAuthToken

from tests import IGittTestCase


class TestInterfacesInit(IGittTestCase):

    def test_raises_runtime_error(self):

        @error_checked_request
        def return_300():
            return '', 300

        try:
            return_300()
        except RuntimeError as ex:
            self.assertEqual(ex.args, ('', 300))

    @staticmethod
    def test_get_query_gitlab():
        token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        _fetch(GITLAB_BASE_URL, 'get', token,
               '/projects', query_params={'owned': True})

    @staticmethod
    def test_pagination():
        # this is to cover the branch where it handles the pagination
        token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        _fetch(GITHUB_BASE_URL, 'get', token, '/repos/coala/corobo/issues')

    @staticmethod
    def test_github_search_pagination():
        # this is to cover the pagination format from github search API
        token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        _fetch(GITHUB_BASE_URL, 'get', token,
               '/search/issues', query_params={'q': ' repo:coala/corobo'})
