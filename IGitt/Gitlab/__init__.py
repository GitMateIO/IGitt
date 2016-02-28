"""
This package contains the Gitlab implementations of the interfaces in
server.git.Interfaces.
"""

from json import loads

from requests import delete, get, patch, post

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
