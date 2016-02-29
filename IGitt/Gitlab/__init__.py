"""
This package contains the Gitlab implementations of the interfaces in
server.git.Interfaces.
"""

from json import loads

from requests import get

HEADERS = {'User-Agent': 'GitMate'}


def query(token: str, url: str):
    """
    Queries Gitlab on the given URL for data.

    :param token: A private token.
    :param url: E.g. ``/projects``
    :return: A dictionary with the data.
    """
    return loads(get('https://gitlab.com/api/v3/' + url,
                     params={'private_token': token},
                     headers=HEADERS).text)


def delete_request(token: str, url: str):
    """
    Sends a delete request to the given URL on Gitlab.

    :param token: A private token.
    :param url: The URL to access, e.g. ``/projects``.
    """
    delete('https://gitlab.com/api/v3/' + url, params={'private_token': token},
           headers=HEADERS)
