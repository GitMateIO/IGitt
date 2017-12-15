from unittest.mock import PropertyMock
from unittest.mock import patch

from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces.Repository import Repository

from tests import IGittTestCase


class TestMergeRequest(IGittTestCase):

    def setUp(self):
        self.mr = MergeRequest()
        self.repo = Repository()

    @patch.object(Repository, 'hoster', new_callable=PropertyMock)
    @patch.object(Repository, 'full_name', new_callable=PropertyMock)
    @patch.object(MergeRequest, 'repository', new_callable=PropertyMock)
    def test_get_keywords_issues(self, mock_repository, mock_full_name,
                                 mock_hoster):
        mock_hoster.return_value = 'github'
        mock_full_name.return_value = 'gitmate-test-user/test'
        mock_repository.return_value = self.repo

        test_cases = [
            ({('123', 'gitmate-test-user/test')},
             ['https://github.com/gitmate-test-user/test/issues/123']),
            ({('234', 'gitmate-test-user/test/repo')},
             ['gitmate-test-user/test/repo#234']),
            ({('345', 'gitmate-test-user/test')},
             ['gitmate-test-user/test#345']),
            ({('456', 'gitmate-test-user/test')},
             ['#456']),

            ({('345', 'gitmate-test-user/test')},
             ['hey there [#123](https://github.com/gitmate-test-user/test/issues/345)'])
        ]

        for expected, body in test_cases:
            self.assertEqual(
                self.mr._get_keywords_issues(r'', body),
                expected
            )

        bad = [
            '[#123]',
            '#123ds',
            'https://saucelabs.com/beta/tests/18c6aed24ed143d3bd1d1096498f34ac/commands#178',
        ]

        for body in bad:
            self.assertEqual(self.mr._get_keywords_issues(r'', body), set())
