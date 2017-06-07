import unittest

from IGitt.Interfaces.CommitStatus import Status
from IGitt.Interfaces.Commit import Commit


class TestCommit(unittest.TestCase):

    def test_status(self):
        CommitMock = type('CommitMock', (Commit, ),
                          {'set_status': lambda self, s: self.statuses.append(s),
                           'get_statuses': lambda self: self.statuses,
                           'statuses': []})

        commit = CommitMock()
        commit.pending()
        assert commit.get_statuses()[0].context == 'review/gitmate/manual'

        commit.ack()
        assert commit.get_statuses()[1].status == Status.SUCCESS
        commit.unack()
        assert commit.get_statuses()[2].status == Status.FAILED
        commit.pending()
        assert len(commit.get_statuses()) == 3
