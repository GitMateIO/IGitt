import os

from IGitt.Interfaces import _fetch
from IGitt.Interfaces import error_checked_request
from IGitt.GitHub import BASE_URL as GITHUB_BASE_URL
from IGitt.GitLab import BASE_URL as GITLAB_BASE_URL

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

    def test_get_query_gitlab(self):
        _fetch(GITLAB_BASE_URL, 'get',
                {'access_token': os.environ.get('GITLAB_TEST_TOKEN', '')},
                '/projects', query_params={'owned': True})

    def test_pagination(self):
        # this is to cover the branch where it handles the pagination
        _fetch(GITHUB_BASE_URL, 'get',
                {'access_token': os.environ.get('GITHUB_TEST_TOKEN', '')},
                '/repos/coala/corobo/issues')

    def test_github_search_pagination(self):
        # this is to cover the pagination format from github search API
        _fetch(GITHUB_BASE_URL, 'get',
               {'access_token': os.environ.get('GITHUB_TEST_TOKEN', '')},
               '/search/issues',
               query_params={'q': ' repo:coala/corobo'})
