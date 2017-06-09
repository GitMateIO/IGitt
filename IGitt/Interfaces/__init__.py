"""
This package contains an abstraction for a git repository.
"""
from functools import wraps
from enum import Enum
from requests import Session


HEADERS = {'User-Agent': 'IGitt'}


def error_checked_request(func):
    """
    Create an error check wrapper augmenting ``func`` to perform the given
    request and check the response for errors.
    """
    @wraps(func)
    def wrap_func(*args, **kwargs):
        """
        Perform the given request and checks the response for errors.
        Any arguments are passed through to ``func``.

        :raises RuntimeError: If the response indicates any problem.
        """
        response, code = func(*args, **kwargs)
        if code >= 300:
            raise RuntimeError(response, code)

        return response
    return wrap_func


@error_checked_request
def _fetch(base_url: str, req_type: str, token: dict, url: str,
           data: dict=None, query_params: dict=None):
    """
    Fetch all the contents by following
    the ``Link`` header.

    :param base_url: The base URL which is used to generate sub URLs.
    :param req_type: A request type. Get, Post, Patch and Delete.
    :param token: A dict with matching query parameter and oauth token.
    :param url  : E.g. ``/repo``
    :param query_params: The query parameters.
    :param data : The data to post. Used for Patch and Post methods only
    :return     : A dictionary or a list of dictionary if the response contains
                  multiple items (usually in case of pagination) and the HTTP
                  status code.
    """
    data_container = []
    req = Session()
    req_methods = {
        'get': req.get,
        'post': req.post,
        'put': req.put,
        'patch': req.patch,
        'delete': req.delete
    }
    req.params.update(HEADERS)
    req.params.update(token)
    if query_params is not None:
        req.params.update(query_params)
    fetch_method = req_methods[req_type]
    resp = fetch_method(base_url + url, json=data)

    # Delete request returns no response
    if not len(resp.text):
        return [], resp.status_code
    if isinstance(resp.json(), dict):
        return resp.json(), resp.status_code
    while resp.links.get('next', False):
        data_container.extend(resp.json())
        resp = fetch_method(resp.links.get('next')['url'], json=data)

    # Add the last node data
    data_container.extend(resp.json())
    return data_container, resp.status_code


class AccessLevel(Enum):
    """
    Different access levels for users.
    """
    CAN_VIEW = 10
    CAN_READ = 20
    CAN_WRITE = 30
    ADMIN = 40
    OWNER = 50
