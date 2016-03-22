"""
This package contains the Gitlab implementations of the interfaces in
server.git.Interfaces.
"""

from requests import Session

HEADERS = {'User-Agent': 'GitMate'}
BASE_URL = "https://gitlab.com/api/v3"


def _fetch_all(req_type: str, token: str, url: str, data: dict=None):
    """
    Fetch all the contents by following
    the ``Link`` header.

    :param req_type: A request type. Get, Post, Patch and Delete.
    :param token: A private token.
    :param url  : E.g. ``/repo``
    :param data : The data to post. Used for Patch and Post methods only
    :return     : A dictionary or a list of dictionary if the response contains
                  multiple items ( usually in case of pagination )
    """

    data_container = []
    req = Session()
    req_methods = {
        'get': req.get,
        'post': req.post,
        'patch': req.patch,
        'delete': req.delete}
    params = {'private_token': token}
    req.params.update(params)
    req.headers.update(HEADERS)
    fetch_method = req_methods[req_type]
    resp = fetch_method(BASE_URL + url, json=data)

    # Delete request returns no response
    if not len(resp.text):
        return
    if isinstance(resp.json(), dict):
        return resp.json()
    while resp.links.get('next', False):
        data_container.extend(resp.json())
        resp = fetch_method(resp.links.get('next')['url'], json=data)

    # Add the last node data
    data_container.extend(resp.json())
    return data_container


def get(token: str, url: str):
    """
    Queries Gitlab on the given URL for data.

    :param token: A private token.
    :param url: E.g. ``/projects``
    :return: A dictionary with the data.
    """
    return _fetch_all('get', token, url)


def post(token: str, url: str, data: dict):
    """
    Posts the given data onto Gitlab.

    :param token: A private token.
    :param url: The URL to access, e.g. ``/projects``.
    :param data: The data to post.
    :return: The response as a dictionary.
    """
    return _fetch_all('post', token, url, data)


def patch(token: str, url: str, data: dict):
    """
    Patches the given data onto Gitlab.

    :param token: A private token.
    :param url: The URL to access, e.g. ``/projects``.
    :param data: The data to post.
    :return: The response as a dictionary.
    """
    return _fetch_all('patch', token, url, data)


def delete(token: str, url: str):
    """
    Sends a delete request to the given URL on Gitlab.

    :param token: A private token.
    :param url: The URL to access, e.g. ``/projects``.
    """
    _ = _fetch_all('delete', token, url)
