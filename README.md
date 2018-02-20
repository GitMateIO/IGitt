.. image:: .gitlab/logo_256.png

IGitt
=====

This is a simple library that allows you to access various git hosting
services like GitHub, GitLab and so on via one unified python interface.

Nice, huh?

What About the Name?
--------------------

This is an **I**\ nterface for **Git** hosting services. Igitt itself
comes from the german language and can be defined "an exclamation of
disgust in regards to an offensive odor, taste, sight, or thought".

Maintenance
-----------

IGitt is maintained by Lasse Schuirmann (lasse.schuirmann@gmail.com).

Installation
------------
Use Python3!


```
sudo apt install python-pip  # Install pip
pip install -r requirements.txt  # Install requirements
pip install .  # Install IGitt
```

Testing
-------

- Open a GitHub test repo
- Open a test issue
- Get the GitHub Token: https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/
- Run Python in your terminal
- Perform what you want to perform. In the following example we will manually set labels for a given issue:


```
In [1]: from IGitt.GitHub.GitHubIssue import GitHubToken, GitHubIssue  # Import the required functions

In [2]: InstanceOfIssue = GitHubIssue(GitHubToken("INSERT YOUR TOKEN"), "INSERT REPO", INSERT ISSUE NUMBER)  # Create an instance of the Issue

In [3]: InstanceOfIssue = GitHubIssue(GitHubToken("INSERT YOUR TOKEN"), "INSERT REPO", 10)  # Create an instance of the Issue

In [4]: InstanceOfIssue.labels = {"First Label"}  # Set a label

In [5]: InstanceOfIssue.labels = {"First Label", "Second Label"}  # Set more labels

In [6]: InstanceOfIssue.labels  # Show labels set
Out[6]: {"First Label", "Second Label"}
```
