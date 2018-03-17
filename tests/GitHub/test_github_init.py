import asyncio

from IGitt.GitHub import GitHubToken, BASE_URL
from IGitt.Interfaces import lazy_get

from tests import IGittTestCase


class GitHubInitTest(IGittTestCase):

    def test_tokens(self):
        github_token = GitHubToken('test')
        self.assertEqual(github_token.parameter, {'access_token': 'test'})
        self.assertEqual(github_token.value, 'test')

    async def lazy_get_response(self, data):
        self.assertEqual(data[0]['total'], 1)

    def test_lazy_get(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(lazy_get(
            BASE_URL + '/repos/gitmate-test-user/test/stats/contributors',
            self.lazy_get_response))
