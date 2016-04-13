"""
This contains the Issue implementation for Gitlab.
"""

from IGitt.Gitlab import get, post, put
from IGitt.Gitlab.GitlabComment import GitlabComment
from IGitt.Interfaces.Issue import Issue


class GitlabIssue(Issue):
    """
    This class represents an issue on Gitlab.
    """

    def __init__(self, private_token: str, project_id: int, issue_id: int):
        """
        Creates a new GitlabIssue with the given credentials.

        :param private_token: The private token.
        :param project_id: The project id.
        :param issue_id: The issue id.
        :raises RuntimeError: If something goes wrong (network, auth, ...)
        """
        self._token = private_token
        self._project = project_id
        self._url = '/projects/'+str(project_id)+'/issues/'+str(issue_id)
        self._data = get(self._token, self._url)

    @property
    def title(self):
        """
        Retrieves the title of the issue.

        >>> from os import environ
        >>> issue = GitlabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     915800, 1274759)
        >>> issue.title
        'test issue title'


        You can simply set it using the property setter:

        >>> issue.title = 'dont panic'
        >>> issue.title
        'dont panic'

        >>> issue.title = 'test issue title'

        :return: The title of the issue - as string.
        """
        return self._data['title']

    @title.setter
    def title(self, new_title):
        """
        Sets the title of the issue.

        :param new_title: The new title.
        """
        self._data = put(self._token, self._url, {'title': new_title})

    @property
    def number(self) -> int:
        """
        Returns the issue id.

        >>> from os import environ
        >>> issue = GitlabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     915800, 1274759)
        >>> issue.number
        1274759

        :return: The id of the issue.
        """
        return self._data['id']

    @property
    def assignee(self):
        """
        Retrieves the assignee of the issue:

        >>> from os import environ
        >>> issue = GitlabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     915800, 1274759)
        >>> issue.assignee
        'GitMateTest'

        >>> issue = GitlabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     915800, 1455638,)
        >>> issue.assignee  # Returns None, unassigned

        :return: A string containing the username or None.
        """
        return (self._data['assignee']['username'] if self._data['assignee'] else
                None)

    @property
    def description(self):
        """
        Retrieves the main description of the issue:

        >>> from os import environ
        >>> issue = GitlabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     915800, 1274759)
        >>> issue.description
        'some text issue text'

        :return: A string containing the main description of the issue.
        """
        return self._data['description']

    def add_comment(self, body):
        """
        Adds a comment to the issue:

        >>> from os import environ
        >>> issue = GitlabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     915800, 1274759)
        >>> comment = issue.add_comment("Doh!")

        You can use the comment right after:

        >>> comment.body
        'Doh!'

        comment.delete() can't test this as the Gitlab api does not support it

        The comment will be created by the user authenticated via the oauth
        token.

        :param body: The body of the new comment to create.
        :return: The newly created comment.
        """
        result = post(self._token, self._url + '/notes', {'body': body})

        return GitlabComment(
            self._token, self._project, self._data['id'], result['id'])

    @property
    def labels(self):
        """
        Retrieves all labels associated with this bug.

        >>> from os import environ
        >>> issue = GitlabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     915800, 1274759)
        >>> issue.labels
        set()

        Use the property setter to set the labels:

        >>> issue.labels = {'test label 1', 'test label 2'}
        >>> sorted(issue.labels)
        ['test label 1', 'test label 2']

        Use the empty set intuitively to clear all labels:

        >>> issue.labels = set()

        :return: A list of label captions (str).
        """
        return self._data['labels']

    @labels.setter
    def labels(self, value: {str}):
        """
        Sets the labels to the given set of labels.

        :param value: A set of label texts.
        """
        self._data = put(self._token, self._url, {'labels': list(value)})

    @property
    def available_labels(self):
        """
        Retrieves a set of captions that are available for labelling bugs.

        >>> from os import environ
        >>> issue = GitlabIssue(environ['GITLAB_TEST_TOKEN'],
        ...                     915800, 1274759)
        >>> sorted(issue.available_labels)
        ['test label 1', 'test label 2']

        :return: A set of label captions (str).
        """
        return {label['name'] for label in get(
            self._token, '/projects/' + self._project + '/labels')}
