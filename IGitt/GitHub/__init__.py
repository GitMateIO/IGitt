"""
This package contains the GitHub implementations of the interfaces in
server.git.Interfaces.
"""

from json import loads

from requests import delete, get, patch, post

HEADERS = {'User-Agent': 'GitMate'}


def query(token: str, url: str):
    """
    Queries GitHub on the given URL for data.

    :param token: An OAuth token.
    :param url: E.g. ``/repo``
    :return: A dictionary with the data.
    """
    return loads(get('https://api.github.com' + url,
                     params={'access_token': token},
                     headers=HEADERS).text)


def post_data(token: str, url: str, data: dict):
    """
    Posts the given data onto GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param data: The data to post.
    :return: The response as a dictionary.
    """
    return loads(post('https://api.github.com' + url,
                      params={'access_token': token}, headers=HEADERS,
                      json=data).text)


def patch_data(token: str, url: str, data: dict):
    """
    Patches the given data onto GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    :param data: The data to post.
    :return: The response as a dictionary.
    """
    return loads(patch('https://api.github.com' + url,
                       params={'access_token': token}, headers=HEADERS,
                       json=data).text)


def delete_request(token: str, url: str):
    """
    Sends a delete request to the given URL on GitHub.

    :param token: An OAuth token.
    :param url: The URL to access, e.g. ``/repo``.
    """
    delete('https://api.github.com' + url, params={'access_token': token},
           headers=HEADERS)
