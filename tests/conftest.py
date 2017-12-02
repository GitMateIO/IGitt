import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--record-cassettes',
        action='store',
        default='once',
        help=('Modify vcrpy cassette recording mode. Allowed options are '
              'once (record cassettes once), '
              'new_episodes (records only new cassettes and replay old ones), '
              'none (only replay previous cassettes) and '
              'all (record everything, never replay recorded interactions).'))


@pytest.fixture(scope='class')
def vcrpy_record_mode(request):
    request.cls.vcrpy_record_mode = request.config.getoption(
        '--record-cassettes')
