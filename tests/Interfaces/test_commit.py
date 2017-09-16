import unittest

from IGitt.Interfaces.CommitStatus import Status
from IGitt.Interfaces.Commit import Commit


class TestCommit(unittest.TestCase):

    def test_status(self):
        CommitMock = type('CommitMock', (Commit, ),
                          {'set_status': lambda self, s: self.statuses.append(s),
                           'get_statuses': lambda self: self.statuses,
                           'statuses': [],
                           'combined_status': Status.SUCCESS,
                           'comment': lambda self: None,
                           'message': lambda self: 'random message',
                           'parent': lambda self: None,
                           'repository': lambda self: None,
                           'sha': lambda self: None,
                           'unified_diff': lambda self: None})

        commit = CommitMock() #pylint: disable=E0110
        commit.pending()
        assert commit.get_statuses()[0].context == 'review/gitmate/manual'

        commit.ack()
        assert commit.get_statuses()[1].status == Status.SUCCESS
        commit.unack()
        assert commit.get_statuses()[2].status == Status.FAILED
        commit.pending()
        assert len(commit.get_statuses()) == 3
