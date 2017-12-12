"""
This module contains the Actions classes representing the actions which
could be taken on webhooks.
"""
from enum import Enum


class MergeRequestActions(Enum):
    """
    Merge Request related actions.
    """
    # When a new merge request is created.
    OPENED = 1
    # When an existing merge request is closed.
    CLOSED = 2
    # When an existing merge request is reopened.
    REOPENED = 3
    # When someone comments on the merge request.
    COMMENTED = 4
    # When a merge request gets assigned or reassigned, labels are added or
    # removed or a milestone is changed
    ATTRIBUTES_CHANGED = 5
    # When someone pushes to an existing merge request.
    SYNCHRONIZED = 6
    # When an existing merge request is merged.
    MERGED = 7
    # When a label is added to the merge request.
    LABELED = 8
    # When a label is removed from the merge request.
    UNLABELED = 9


class IssueActions(Enum):
    """
    Issue related reactions.
    """
    # When a new issue is opened.
    OPENED = 1
    # When an existing issue is closed.
    CLOSED = 2
    # When an existing issue is reopened.
    REOPENED = 3
    # When someone comments on an issue.
    COMMENTED = 4
    # When an issue gets reassigned, or the linked
    # milestone is changed
    ATTRIBUTES_CHANGED = 5
    # When a new label is added to the issue
    LABELED = 6
    # When a label is removed from an issue
    UNLABELED = 7

class PipelineActions(Enum):
    """
    Pipeline and Commit status related actions.
    """
    # When the status of a pipeline is updated, also depicts the change of a
    # commit status
    UPDATED = 1


class InstallationActions(Enum):
    """
    Installation and Integration related actions.
    """
    # When an app is installed.
    CREATED = 1
    # When an app is uninstalled.
    DELETED = 2
    # When a repository/repositories are added to an installation.
    REPOSITORIES_ADDED = 3
    # When a repository/repositories are removed from an installation.
    REPOSITORIES_REMOVED = 4
