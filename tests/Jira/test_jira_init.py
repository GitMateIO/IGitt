from os import environ

from IGitt.Jira import JiraToken
from IGitt.Jira import get

from tests import IGittTestCase


class JiraInitTest(IGittTestCase):

    def setUp(self):
        self.token = JiraToken(environ.get('JIRA_CLIENT_KEY', ''),
                               environ.get('JIRA_TEST_TOKEN', ''),
                               environ.get('JIRA_TEST_SECRET', ''))

    def test_get(self):
        projects = {project['name'] for project in get(self.token, '/project')}
        self.assertEqual({'Kanban Example', 'Lasse Test Kanban'}, projects)
