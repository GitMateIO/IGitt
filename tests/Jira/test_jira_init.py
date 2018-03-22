from os import environ

from IGitt.Jira import JiraOAuth1Token, BASE_URL
from IGitt.Interfaces import get

from tests import IGittTestCase


class JiraInitTest(IGittTestCase):

    def test_tokens(self):
        token = JiraOAuth1Token(environ['JIRA_CLIENT_KEY'],
                                environ['JIRA_TEST_TOKEN'],
                                environ['JIRA_TEST_SECRET'])
        self.assertEqual(token.parameter, {})
        self.assertEqual(token.value, {
            'client_key': environ['JIRA_CLIENT_KEY'],
            'oauth_token': environ['JIRA_TEST_TOKEN'],
            'oauth_token_secret': environ['JIRA_TEST_SECRET'],
        })
        self.assertEqual(get(token, BASE_URL + '/myself')['name'],
                         'nkprince007')
