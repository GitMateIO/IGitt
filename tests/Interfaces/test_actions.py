import unittest

from IGitt.Interfaces.Actions import MergeRequestActions, IssueActions


class TestActions(unittest.TestCase):

    def test_mr_actions(self):
        mr = MergeRequestActions(1)
        self.assertEqual(mr.name, 'OPENED')

    def test_issue_actions(self):
        iss = IssueActions(2)
        self.assertEqual(iss.name, 'CLOSED')
