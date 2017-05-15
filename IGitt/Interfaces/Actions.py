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
    # When an issue gets reassigned, labels are added or removed or the linked
    # milestone is changed
    ATTRIBUTES_CHANGED = 5
