"""
This package contains abstractions to use git, as well as services providing
hosting for it (GitHub, GitLab and others).
"""


class ElementDoesntExistError(Exception):
    """
    Indicates that the desired element doesn't exist.
    """


class ElementAlreadyExistsError(Exception):
    """
    Indicates that the element (that is probably to be created) already exists.
    """
