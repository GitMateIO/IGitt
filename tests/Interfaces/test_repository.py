from unittest.mock import MagicMock

import git

from IGitt.Interfaces.Repository import Repository

git.Repo.clone_from = MagicMock()
git.Repo.clone_from.return_value = git.Repo()

test_repo = type('MockRepo', (Repository, ),
                 {'clone_url': 'https://github.com/sils/configurations',
                  'create_file': lambda self: None,
                  'create_fork': lambda self: None,
                  'create_issue': lambda self: None,
                  'create_label': lambda self: None,
                  'create_merge_request': lambda self: None,
                  'delete': lambda self: None,
                  'delete_hook': lambda self: None,
                  'delete_label': lambda self: None,
                  'filter_issues': lambda self: None,
                  'full_name': lambda self: None,
                  'get_issue': lambda self: None,
                  'get_labels': lambda self: None,
                  'get_mr': lambda self: None,
                  'hooks': lambda self: None,
                  'hoster': lambda self: None,
                  'issues': lambda self: None,
                  'merge_requests': lambda self: None,
                  'register_hook': lambda self: None,
                  'search_issues': lambda self: None,
                  'search_mrs': lambda self: None})

repo, path = test_repo().get_clone() #pylint: disable=E0110

assert isinstance(repo, git.Repo)
assert 'tmp' in path
