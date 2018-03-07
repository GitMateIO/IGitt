from unittest.mock import MagicMock

import git

from IGitt.Interfaces.Repository import Repository
from tests import IGittTestCase


class TestRepository(IGittTestCase):

    def setUp(self):
        git.Repo.clone_from = MagicMock()
        git.Repo.clone_from.return_value = git.Repo()

        self.test_repo = type(
            'MockRepo', (Repository, ),
            {'clone_url': 'https://github.com/sils/configurations'})


    def test_clone(self):
        repo, path = self.test_repo().get_clone()

        self.assertIsInstance(repo, git.Repo)
        self.assertIn('tmp', path)
