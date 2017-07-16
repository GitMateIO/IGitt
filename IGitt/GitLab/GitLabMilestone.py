"""
This contains the Milestone implementation for GitLab
"""
#from datetime import datetime
from urllib.parse import quote_plus

from IGitt.GitLab import GitLabMixin
#from IGitt.GitLab import get
from IGitt.GitLab import put
from IGitt.GitLab import post
from IGitt.GitLab import GitLabOAuthToken, GitLabPrivateToken
#from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.Milestone import Milestone

class GitLabMilestone(Milestone, GitLabMixin):
    """
    This class represents a milestone on GitLab.
    """

    def __init__(self, token: (GitLabOAuthToken, GitLabPrivateToken),
                 repository: str, number: int):
        """
        Creates a new GitLabMilestone with the given credentials.

        :param token: A Token object to be used for authentication.
        :param repository: The full name of the repository.
                           e.g. ``sils/baritone``.
        :param number: The milestone's id. Note that it is not the iid but the
        id.
        :raises RuntimeError: If something goes wrong (network, auth, ...)
        """
        self._token = token
        self._repository = repository
        self._id = number
        self._url = '/projects/{repo}/milestones/{milestone_id}'.format(
            repo=quote_plus(repository), milestone_id=number)


    @staticmethod
    def create(token: (GitLabOAuthToken, GitLabPrivateToken), repository: str,
               title: str, body: str=''):
        """
        Create a new milestone with given title and body.

        >>> from os import environ
        >>> milestone = GitLabMilestone.create(
        ...     GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...     'gitmate-test-user/test',
        ...     'test milestone title',
        ...     'sample description'
        ... )
        >>> milestone.state
        'active'

        Delete the milestone to avoid filling the test repo with milestones.

        >>> milestone.close()

        :return: GitLabMilestone object of the newly created milestone.
        """
        url = '/projects/{repo}/milestones'.format(repo=quote_plus(repository))
        milestone = post(token, url, {'title': title, 'description': body})

        return GitLabMilestone(token, repository, milestone['id'])

    @property
    def state(self):
        """
        Get's the state of the milestone.

        >>> from os import environ
        >>> milestone = GitLabMilestone(GitLabOAuthToken(environ['GITLAB_TEST_TOKEN']),
        ...                     'gitmate-test-user/test', 1)
        >>> milestone.state
        'active'
#TODO create milestone to test against
        So if we close it:

        >>> milestone.close()
        >>> milestone.state
        'closed'

        And reopen it:

        >>> milestone.reopen()
        >>> milestone.state
        'active'

        :return: Either 'active' or 'closed'.
        """
        return self.data['state']

    def close(self):
        """
        Closes the milestone.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = put(self._token, self._url, {'state_event': 'close'})


    def reopen(self):
        """
        Reopens the milestone.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        self.data = put(self._token, self._url, {'state_event': 'activate'})
