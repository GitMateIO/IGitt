import os

from IGitt.Interfaces import _fetch
from IGitt.Interfaces import error_checked_request
from IGitt.GitHub import BASE_URL as GITHUB_BASE_URL
from IGitt.GitHub import get
from IGitt.GitHub import GitHubToken
from IGitt.GitHub import GitHubJsonWebToken
from IGitt.GitHub import GitHubInstallationToken
from IGitt.GitLab import BASE_URL as GITLAB_BASE_URL
from IGitt.GitLab import GitLabOAuthToken

from tests import IGittTestCase


class TestInterfacesInit(IGittTestCase):

    def setUp(self):
        self.token = GitHubJsonWebToken(os.environ['GITHUB_PRIVATE_KEY'],
                                        os.environ['GITHUB_TEST_APP_ID'])

    def test_github_json_web_token(self):
        self.assertEqual(self.token.is_expired, False)
        data = get(self.token, '/app')
        self.assertEqual(data['id'], int(os.environ['GITHUB_TEST_APP_ID']))
        self.assertEqual(data['name'], 'gitmate-test-app')

    def test_github_installation_token(self):
        itoken = GitHubInstallationToken(57250, self.token)
        data = get(itoken, '/installation/repositories')
        self.assertEqual(data['total_count'], 1)
        self.assertEqual(data['repositories'][0]['full_name'],
                         'gitmate-test-org/test')
        self.assertEqual(itoken.is_expired, False)

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
