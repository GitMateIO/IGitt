.. image:: .gitlab/logo_256.png

IGitt
=====

This is a simple library that allows you to access various git hosting
services like GitHub, GitLab and so on via one unified python interface.

Installation
------------

Make sure you have Python 3 installed. IGitt will not work with Python 2.

Simply install it with::

    pip install IGitt

Quickstart
----------

All classes follow the APIs given in `IGitt.Interfaces`. Here's an example on
how to set labels on a GitHub issue::

    from IGitt.GitHub.GitHubIssue import GitHubToken, GitHubIssue
    issue = GitHubIssue(GitHubToken("YOUR TOKEN"), "ORG/REPO", NUMBER)

    issue.labels = {"type/bug", "area/core"}

For more documentation you'll have to check the documentation comments for now.

More docs are available at `IGitt.GitMate.io <https://igitt.gitmate.io/>`_.

What About the Name?
--------------------

This is an **I**\ nterface for **Git** hosting services. Igitt itself
comes from the german language and can be defined "an exclamation of
disgust in regards to an offensive odor, taste, sight, or thought".
