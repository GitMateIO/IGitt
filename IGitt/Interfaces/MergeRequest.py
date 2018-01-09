"""
Contains a class that represents a request to merge something into some git
branch.
"""
from datetime import datetime
from itertools import chain
from typing import List
from typing import Set
import re

from IGitt.Interfaces import MergeRequestStates
from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.CommitStatus import Status
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.User import User


SUPPORTED_HOST_KEYWORD_REGEX = {
    'github': (r'[Cc]lose[sd]?'
               r'|[Rr]esolve[sd]?'
               r'|[Ff]ix(?:e[sd])?'),
    'gitlab': (r'[Cc]los(?:e[sd]?|ing)'
               r'|[Rr]esolv(?:e[sd]?|ing)'
               r'|[Ff]ix(?:e[sd]|ing)?')
    }
CONCATENATION_KEYWORDS = [r',', r'\sand\s']


class MergeRequest(Issue):
    """
    A request to merge something into the main codebase. Can be a patch in a
    mail or a pull request on GitHub.
    """

    def close(self):
        """
        Closes the merge request.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    def reopen(self):
        """
        Reopens the merge request.

        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        raise NotImplementedError

    @property
    def state(self) -> MergeRequestStates:
        """
        Get's the state of the merge request.

        :return: A MergeRequestStates object indicating current state.
        """
        raise NotImplementedError

    @property
    def base(self) -> Commit:
        """
        Retrieves the base commit of the merge request, i.e. the one it should
        be merged into.

        :return: A Commit object.
        """
        raise NotImplementedError

    @property
    def base_branch_name(self) -> str:
        """
        Retrieves the base branch name of the merge request, i.e. the one it
        should be merged into.

        :return: A string.
        """
        raise NotImplementedError

    @property
    def head(self) -> Commit:
        """
        Retrieves the head commit of the merge request, i.e. the one which
        would be merged.

        :return: A Commit object.
        """
        raise NotImplementedError

    @property
    def head_branch_name(self) -> str:
        """
        Retrieves the head branch name of the merge request, i.e. the one that
        will be merged.

        :return: A string.
        """
        raise NotImplementedError

    @property
    def commits(self) -> List[Commit]:
        """
        Retrieves all commits that are contained in this request.

        :return: A list of Commits.
        """
        raise NotImplementedError

    @property
    def repository(self):
        """
        Retrieves the repository where this PR is opened at.

        :return: A Repository object.
        """
        raise NotImplementedError

    @property
    def target_repository(self):
        """
        Retrieves the repository where this PR is opened at. An alias to
        ``self.repository`` property.

        :return: A Repository object.
        """
        return self.repository

    @property
    def source_repository(self):
        """
        Retrieves the repository where this PR's head branch is located at.

        :return: A Repository object.
        """
        raise NotImplementedError

    @property
    def affected_files(self):
        """
        Retrieves the affected files.

        :return: A set of filenames relative to repo root.
        """
        raise NotImplementedError

    @property
    def diffstat(self):
        """
        Gets additions and deletions of a merge request.

        :return: An (additions, deletions) tuple.
        """
        raise NotImplementedError

    @property
    def created(self) -> datetime:
        """
        Retrieves a timestamp on when the merge request was created.
        """
        raise NotImplementedError

    @property
    def updated(self) -> datetime:
        """
        Retrieves a timestamp on when the merge request was updated the last
        time.
        """
        raise NotImplementedError

    @property
    def number(self) -> int:
        """
        Returns the MR "number" or id.
        """
        raise NotImplementedError

    # Ignore PyLintBear
    def _get_keywords_issues(self, keyword: str, body_list: List) -> Set[int]:
        """
        Returns a set of tuples(issue number, name of the repository the issue
        is contained in), which are mentioned with given ``keyword``.
        """
        results = set()
        hoster = self.repository.hoster
        repo_name = self.repository.full_name

        identifier_regex = r'[\w\.-]+'
        namespace_regex = r'(?:{0})/(?:{0})(?:/(?:{0}))?'.format(
            identifier_regex)
        concat_regex = '|'.join(kw for kw in CONCATENATION_KEYWORDS)
        issue_no_regex = r'[1-9][0-9]*'
        issue_url_regex = r'https?://{}\S+/issues/{}'.format(
            hoster, issue_no_regex)
        c_joint_regex = re.compile(
            r'((?:{0})'         # match keywords expressed via ``keyword``

            r'(?:(?:{3})?\s*'   # match conjunctions
                                # eg: ',', 'and' etc.

            r'(?:(?:\S*)#{2}|'  # match short references
                                # eg: #123, coala/example#23

            r'(?:{1})))+)'      # match full length issue URLs
                                # eg: https://github.com/coala/coala/issues/23

            r''.format(keyword,
                       issue_url_regex, issue_no_regex, concat_regex))
        c_issue_capture_regex = re.compile(
            r'(?:(?:\s+|^)({2})?#({0}))|(?:https?://{1}\S+?/({2})/issues/({0}))'
            ''.format(
                issue_no_regex, hoster, namespace_regex))

        for body in body_list:
            matches = c_joint_regex.findall(body.replace('\r', ''))
            refs = list(chain(*[c_issue_capture_regex.findall(match)
                                for match in matches]))
            for ref in refs:
                if ref[0] != '':
                    repo_name = ref[0]
                if ref[1] != '':
                    results.add((ref[1], repo_name))
                if ref[2] != '' and ref[3] != '':
                    results.add((ref[3], ref[2]))

        return results

    def _get_closes_issues(self) -> Set[int]:
        """
        Returns a set of tuples(issue number, name of the repository the issue
        is contained in), which would be closed upon merging this pull request.
        """
        hoster = self.repository.hoster

        # If the hoster does not support auto closing issues with matching
        # keywords, just return an empty set. At the moment, we only have
        # support for GitLab and GitHub. And both of them support autoclosing
        # issues with matching keywords.
        if hoster not in SUPPORTED_HOST_KEYWORD_REGEX: # dont cover
            return set()

        relevant_texts = [commit.message for commit in self.commits]
        relevant_texts.extend([self.description, self.title])
        return self._get_keywords_issues(
            SUPPORTED_HOST_KEYWORD_REGEX[self.repository.hoster],
            relevant_texts
        )

    def _get_mentioned_issues(self):
        """
        Returns a set of tuples(issue number, name of the repository the issue
        is contained in), which are related to this pull request.
        """
        commit_bodies = [commit.message for commit in self.commits]
        comment_bodies = [comment.body for comment in self.comments]
        return self._get_keywords_issues(r'', commit_bodies + comment_bodies)

    @property
    def closes_issues(self) -> Set[Issue]:
        """
        Returns a set of Issue objects which would be closed upon merging this
        pull request.
        """
        raise NotImplementedError

    @property
    def tests_passed(self) -> bool:
        """
        Returns True if all commits of the merge request have a success state.
        If you wish to only get the head state, use mr.head.combined_status.
        """
        statuses = set(map(lambda commit: commit.combined_status,
                           self.commits))
        if Status.PENDING in statuses or Status.FAILED in statuses:
            return False
        return True

    @property
    def mentioned_issues(self) -> Set[Issue]:
        """
        Returns a set of Issue objects which are related to the pull request.
        """
        raise NotImplementedError

    @property
    def author(self) -> User:
        """
        Returns the author of the MR wrapped in a User object.
        """
        raise NotImplementedError

    def merge(self, message: str=None, sha: str=None,
              should_remove_source_branch: bool=False,
              _github_merge_method: str=None,
              _gitlab_merge_when_pipeline_succeeds: bool=False):
        """
        Merges the merge request.

        :param message:                     The commit message.
        :param sha:                         The commit sha that the HEAD must
                                            match in order to merge.
        :param should_remove_source_branch: Whether the source branch should be
                                            removed upon a successful merge.
        :param _github_merge_method:        On GitHub, the merge method to use
                                            when merging the MR. Can be one of
                                            `merge`, `squash` or `rebase`.
        :param _gitlab_wait_for_pipeline:   On GitLab, whether the MR should be
                                            merged immediately after the
                                            pipeline succeeds.
        :raises RuntimeError:        If something goes wrong (network, auth...).
        :raises NotImplementedError: If an unused parameter is passed.
        """
        raise NotImplementedError
