from unittest.mock import MagicMock

import git

from IGitt.Interfaces.Repository import Repository

git.Repo.clone_from = MagicMock()
git.Repo.clone_from.return_value = git.Repo()

test_repo = type('MockRepo', (Repository, ),
                 {'clone_url': 'https://github.com/sils/configurations'})

repo, path = test_repo().get_clone()

assert isinstance(repo, git.Repo)
assert 'tmp' in path
