import os

from IGitt.GitHub import BASE_URL as GITHUB_BASE_URL
from IGitt.GitHub import GitHubToken
from IGitt.GitHub import GitHubJsonWebToken
from IGitt.GitHub import GitHubInstallationToken
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitLab import BASE_URL as GITLAB_BASE_URL
from IGitt.GitLab import GitLabOAuthToken
from IGitt.Interfaces import _RESPONSES
from IGitt.Interfaces import _fetch
from IGitt.Interfaces import get
from IGitt.Interfaces import BasicAuthorizationToken

from tests import IGittTestCase


class TestInterfacesInit(IGittTestCase):

    def setUp(self):
        self.token = GitHubJsonWebToken(os.environ['GITHUB_PRIVATE_KEY'],
                                        os.environ['GITHUB_TEST_APP_ID'])

    def test_github_json_web_token(self):
        data = get(self.token, GITHUB_BASE_URL + '/app')
        self.assertEqual(data['id'], int(os.environ['GITHUB_TEST_APP_ID']))
        self.assertEqual(data['name'], 'gitmate-test-app')

    def test_github_installation_token(self):
        itoken = GitHubInstallationToken(60731, self.token)
        data = get(itoken, GITHUB_BASE_URL + '/installation/repositories')
        self.assertEqual(data['total_count'], 1)
        self.assertEqual(data['repositories'][0]['full_name'],
                         'gitmate-test-org/test')
        self.assertEqual(itoken.jwt, self.token)

    def test_raises_runtime_error(self):
        try:
            token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
            _fetch(GITHUB_BASE_URL + '/repos/gitmate-test-user/wontexist',
                   'get', token)
        except RuntimeError as ex:
            self.assertEqual(
                ex.args[0],
                '{"message":"Not Found",'
                '"documentation_url":"https://developer.github.com/v3"}')
            self.assertEqual(ex.args[1], 404)

    @staticmethod
    def test_get_query_gitlab():
        token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        _fetch(GITLAB_BASE_URL + '/projects', 'get', token,
               query_params={'owned': True})

    @staticmethod
    def test_pagination():
        # this is to cover the branch where it handles the pagination
        token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        _fetch(GITHUB_BASE_URL + '/repos/coala/corobo/issues', 'get', token)

    @staticmethod
    def test_github_search_pagination():
        # this is to cover the pagination format from github search API
        token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        _fetch(GITHUB_BASE_URL + '/search/issues', 'get', token,
               query_params={'q': ' repo:coala/corobo'})

    @staticmethod
    def test_github_conditional_request():
        token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        repo = GitHubRepository(token, os.environ.get('GITHUB_TEST_REPO',
                                                      'gitmate-test-user/test'))

        repo.refresh()
        prev_data = repo.data._data
        prev_count = _RESPONSES[repo.url].headers.get('X-RateLimit-Remaining')

        repo.refresh()
        new_data = repo.data._data
        new_count = _RESPONSES[repo.url].headers.get('X-RateLimit-Remaining')

        # check that no reduction in rate limit is observed
        assert prev_count == new_count

        # check that response data hasn't been modified
        assert prev_data == new_data

    def test_basic_authentication_github(self):
        token = BasicAuthorizationToken(
            os.environ.get('GITHUB_TEST_USERNAME', 'gitmate-test-user'),
            os.environ.get('GITHUB_TEST_PASSWORD', 'someuserpassword')
        )
        repo = GitHubRepository(token, 'coala/coala')
        self.assertEqual(repo.identifier, 19816973)
