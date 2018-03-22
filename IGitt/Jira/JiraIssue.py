"""
This contains the Issue implementation for Jira.
"""
from datetime import datetime
from typing import List
from typing import Set
from typing import Union
from urllib.parse import urljoin

from IGitt.Interfaces import get
from IGitt.Interfaces import post
from IGitt.Interfaces import put
from IGitt.Interfaces import IssueStates
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.User import User
from IGitt.Jira import JiraMixin
from IGitt.Jira import JiraOAuth1Token
from IGitt.Jira import JIRA_INSTANCE_URL
from IGitt.Jira.JiraComment import JiraComment


class JiraIssue(JiraMixin, Issue):
    """
    This class represents an Issue resource on JIRA.
    """

    def __init__(self, token: JiraOAuth1Token, identifier: Union[str, int]):
        """
        Instantiates a new JiraIssue object from the given details.

        :param token:
            The OAuth v1.0 token to be used for authentication with JIRA.
        :param identifier:
            The unique identifier or key related to the issue resource.
        """
        self._identifier = identifier
        self._token = token
        self._url = '/issue/{}'.format(identifier)

    @property
    def number(self):
        """
        Retrieves the unique identifier of the issue.

        :return: An integer representing the id of the issue.
        """
        try:
            return int(self._identifier)
        except ValueError:
            return int(self.data['id'])

    @property
    def web_url(self):
        """
        Returns a human accessible web url for the corresponding issue.

        :return:    A string containing the web link for the issue.
        """
        return urljoin(JIRA_INSTANCE_URL,
                       '/browse/{}'.format(self.data['key']))

    @property
    def title(self):
        """
        Retrieves the title or summary of the issue.

        :return: A string containing the title of summary of the issue.
        """
        return self.data['fields']['summary']

    @title.setter
    def title(self, new_title: str):
        """
        Sets the title or summary of the issue to the specified title.

        :param new_title:   The new title to be set on the issue.
        """
        data = {'update': {'summary': [{'set': new_title}]}}
        put(self._token, self.url, data)
        self.data['fields']['summary'] = new_title

    @property
    def description(self):
        """
        Retrieves the description of the issue.

        :return: A string containing the description of the issue.
        """
        return self.data['fields']['description']

    @description.setter
    def description(self, new_description):
        """
        Sets the description of the issue.

        :param new_description: The new description.
        """
        data = {'update': {'description': [{'set': new_description}]}}
        put(self._token, self.url, data)
        self.data['fields']['summary'] = new_description

    @property
    def assignees(self):
        """
        Retrieves the assignees of the issue.

        Note: JIRA only allows one assignee per issue.

        :return: A set of usernames of assignees.
        """
        return {self.data['fields']['assignee']['name']}

    @assignees.setter
    def assignees(self, value: Set[User]):
        """
        Setter for ssignees.
        """
        raise NotImplementedError

    def assign(self, *usernames: List[User]):
        """
        Sets a given users as assignee.
        """
        raise NotImplementedError

    def unassign(self, *usernames: List[User]):
        """
        Unassigns given users from issue.
        """
        raise NotImplementedError

    @property
    def labels(self) -> Set[str]:
        """
        Retrieves the set of labels the issue is currently tagged with.

        :return: The set of labels.
        """
        raise NotImplementedError

    @labels.setter
    def labels(self, value: Set[str]):
        """
        Tags the issue with the given labels. For examples see documentation
        of the labels read function.

        Labels are added and removed as necessary on remote.

        :param value: The new set of labels.
        """
        raise NotImplementedError

    @property
    def available_labels(self) -> Set[str]:
        """
        Compiles a set of labels that are available for labelling this issue.

        :return: A set of label captions.
        """
        raise NotImplementedError

    @property
    def author(self):
        """
        Retrieves the author of the issue.

        :return: A string containing the username of author.
        """
        return self.data['fields']['creator']['name']

    @property
    def comments(self) -> Set[JiraComment]:
        """
        Retrieves the comments on the issue.

        :return: A set of JiraComment instances.
        """
        return {
            JiraComment.from_data(comment,
                                  self._token,
                                  self._identifier,
                                  comment['id'])
            for comment in get(self._token, self.url + '/comment')['comments']
        }

    def add_comment(self, body) -> JiraComment:
        """
        Adds a comment to the issue.

        :param body:            The content of the comment.
        :return:                The newly created comment.
        :raises RuntimeError:   If something goes wrong (network, auth...).
        """
        url = self.url + '/comment'
        resp = post(self._token, url, data={'body': body})
        return JiraComment.from_data(
            resp, self._token, self._identifier, resp['id'])

    @property
    def state(self):
        """
        Retrieves the state of the issue. JIRA determines the state of an issue
        based on ``resolution`` property of issue resource. If ``resolution``
        is ``null``, then the issue is still open, otherwise it has been closed
        or resolved.

        :return:    Either IssueStates.OPEN or IssueStates.CLOSED.
        """
        return (IssueStates.CLOSED if self.data['fields']['resolution']
                else IssueStates.OPEN)

    def close(self):
        """
        Closes the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def reopen(self):
        """
        Reopens the issue.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was created.

        :return:    A datetime.datetime object representing the time of
                    creation of the issue.
        """
        return datetime.strptime(self.data['fields']['created'],
                                 '%Y-%m-%dT%H:%M:%S.%f%z')

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the comment was updated the last time.

        :return:    A datetime.datetime object representing the last updated
                    time of the issue.
        """
        return datetime.strptime(self.data['fields']['updated'],
                                 '%Y-%m-%dT%H:%M:%S.%f%z')

    @property
    def reactions(self) -> List[str]:
        """
        Retrieves the reactions / award emojis applied on the issue.
        """
        raise NotImplementedError

    @property
    def mrs_closed_by(self) -> Set:
        """
        Returns the merge requests that close this issue.
        """
        raise NotImplementedError

    @staticmethod
    def create(token: JiraOAuth1Token,
               project: str,
               issue_type: str,
               title: str,
               body: str):
        """
        Creates a new issue with the given title and body on the specified
        project.

        :param token:
            The OAuth 1.0 token to be used for authentication.
        :param project:
            The identifier of the project in which the issue should be opened.
        :param issue_type:
            The name of the issue type resource to be used.
        :param title:
            The title of the issue.
        :param body:
            The description of the issue.
        :return:
            A new JiraIssue object.
        """
        post_url = '/issue/'
        data = {
            'description': body,
            'fields': {
                'summary': title,
                'issuetype': {'name': issue_type},
                'project': {'id': project}
            }
        }

        resp = post(token, JiraIssue.absolute_url(post_url), data)
        return JiraIssue(token, resp['id'])
