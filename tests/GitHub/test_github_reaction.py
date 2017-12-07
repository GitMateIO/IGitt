import os

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubReaction import GitHubReaction

from tests import IGittTestCase


class GitHubReactionTest(IGittTestCase):

    def setUp(self):
        self.token = GitHubToken(os.environ.get('GITHUB_TEST_TOKEN', ''))
        self.iss = GitHubIssue(self.token, 'gitmate-test-user/test', 12)
        self.reaction = GitHubReaction(self.token, self.iss, 17051518)

    def test_404(self):
        reaction = GitHubReaction(self.token, self.iss, 0)
        with self.assertRaises(RuntimeError):
            reaction.refresh()

    def test_name(self):
        self.assertEqual(self.reaction.name, 'heart')

    def test_user(self):
        self.assertEqual(self.reaction.user.username, 'nkprince007')
