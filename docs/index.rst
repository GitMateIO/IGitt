Welcome to IGitt!
=================

IGitt is a Git hoster abstraction. It is one python API that allows you to rule
over GitHub, GitLab and more hosting platforms.

Why do I Need This?
-------------------

If you want to support more than one hoster it doesn't mean that you want to
implement all your API requests multiple times. With IGitt you can create e.g.
a ``GitHubIssue`` object and use it the same way as a ``GitLabIssue`` object.

Stop worrying about multiple platforms :)

Installation
------------

::

    pip install IGitt

Quickstart
----------

All classes follow the APIs given in `IGitt.Interfaces`. Here's an example on
how to set labels on a GitHub issue::

    from IGitt.GitHub.GitHubIssue import GitHubToken, GitHubIssue
    issue = GitHubIssue(GitHubToken("YOUR TOKEN"), "ORG/REPO", NUMBER)

    issue.labels = {"type/bug", "area/core"}

API Documentation
-----------------

.. toctree::
   :caption: Home
   :hidden:

   Welcome <self>
   Source on GitLab <https://gitlab.com/gitmate/open-source/IGitt>

.. toctree::
   :caption: IGitt API Documentation
   :maxdepth: 4

   IGitt

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
