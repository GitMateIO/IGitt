import os

from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabReaction import GitLabReaction

from tests import IGittTestCase


class GitLabReactionTest(IGittTestCase):

    def setUp(self):
        self.token = GitLabOAuthToken(os.environ.get('GITLAB_TEST_TOKEN', ''))
        self.iss = GitLabIssue(self.token, 'gitmate-test-user/test', 23)
        self.reaction = GitLabReaction(self.token, self.iss, 490941)

    def test_name(self):
        self.assertEqual(self.reaction.name, 'thumbsdown')

    def test_user(self):
        self.assertEqual(self.reaction.user.username, 'nkprince007')
