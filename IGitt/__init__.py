"""
This package contains abstractions to use git, as well as services providing
hosting for it (GitHub, GitLab and others).
"""

from os.path import dirname, join


class ElementDoesntExistError(Exception):
    """
    Indicates that the desired element doesn't exist.
    """


class ElementAlreadyExistsError(Exception):
    """
    Indicates that the element (that is probably to be created) already exists.
    """


with open(join(dirname(__file__), 'VERSION'), 'r') as ver:
    VERSION = ver.readline().strip()
