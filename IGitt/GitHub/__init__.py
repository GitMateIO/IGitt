"""
This package contains the GitHub implementations of the interfaces in
server.git.Interfaces.
"""

from json import loads

from requests import delete as raw_delete
from requests import get as raw_get
from requests import patch as raw_patch
from requests import post as raw_post

HEADERS = {'User-Agent': 'GitMate'}


def get(token: str, url: str):
    """
    Queries GitHub on the given URL for data.

    :param token: An OAuth token.
    :param url: E.g. ``/repo``
    :return: A dictionary with the data.
    """
    return loads(raw_get('https://api.github.com' + url,
                         params={'access_token': token},
                         headers=HEADERS).text)


def post(token: str, url: str, data: dict):
    """
    Posts the given data onto GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param data: The data to post.
    :return: The response as a dictionary.
    """
    return loads(raw_post('https://api.github.com' + url,
                          params={'access_token': token}, headers=HEADERS,
                          json=data).text)


def patch(token: str, url: str, data: dict):
    """
    Patches the given data onto GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param data: The data to post.
    :return: The response as a dictionary.
    """
    return loads(raw_patch('https://api.github.com' + url,
                           params={'access_token': token}, headers=HEADERS,
                           json=data).text)


def delete(token: str, url: str):
    """
    Sends a delete request to the given URL on GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    """
    raw_delete('https://api.github.com' + url, params={'access_token': token},
               headers=HEADERS)
