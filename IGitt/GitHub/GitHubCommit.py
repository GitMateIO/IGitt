"""
Contains the abstraction for a commit in GitHub.
"""
from IGitt import ElementDoesntExistError
from IGitt.GitHub import get, post
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.CommitStatus import CommitStatus, Status

GH_STATE_TRANSLATION = {Status.ERROR: 'error', Status.FAILED: 'failure',
                        Status.PENDING: 'pending', Status.CANCELED: 'failure',
                        Status.SUCCESS: 'success', Status.RUNNING: 'pending'}
INV_GH_STATE_TRANSLATION = {'error': Status.ERROR, 'failure': Status.FAILED,
                            'pending': Status.PENDING,
                            'success': Status.SUCCESS}


def get_diff_index(patch, line_nr):
    r"""
    Takes a patch and receives the position of the given line number in it.

    >>> patch = ('---/version/a\n'
    ...          '+++/version/b\n'
    ...          '@@ -1,2 +1,4 @@\n'
    ...          ' # test\n'  # Line 1
    ...          '+\n'  # Line 2
    ...          '-a test repo\n'  # Line 3
    ...          '+something new\n'  # Line 3
    ...          ' something old\n')  # Line 4
    >>> get_diff_index(patch, 1)
    1
    >>> get_diff_index(patch, 3)
    4
    >>> get_diff_index(patch, 4)
    5

    If the line isn't covered in the patch, it'll return None:

    >>> get_diff_index(patch, 8)

    Sometimes patches contain the function and shall still be interpreted
    correctly:

    >>> patch = ('@@ -464,11 +464,10 @@ def get_action_info(section, action):\n'
    ...          ' line 464\n'
    ...          ' line 465\n'
    ...          ' line 466\n'
    ...          '-line 467\n'
    ...          '-line 468\n'
    ...          '+line 467\n'
    ...          '+line 468\n'
    ...          ' line 469\n')
    >>> get_diff_index(patch, 465)
    2
    >>> get_diff_index(patch, 467)
    6

    :param patch: A list of lines of a unified diff.
    :param line_nr: The line number to identify.
    :return: The position in the Patch or None
    """
    patch = patch.splitlines(True)
    current_line_added = 0
    current_diff_index = 0
    for line in patch:
        if line.startswith('---') or line.startswith('+++'):
            continue

        if line.startswith("@@"):
            values = line[line.find("-"):line.find(" @@", 3)]
            _, added = tuple(values.split(" "))
            current_line_added = int(added.split(",")[0][1:])
        elif line.startswith('+') or line.startswith(' '):
            if current_line_added == line_nr:
                return current_diff_index

            current_line_added += 1

        current_diff_index += 1

    return None


class GitHubCommit(Commit):
    """
    Represents a commit on GitHub.
    """

    def __init__(self, oauth_token: str, repository: str, sha: str):
        """
        Creates a new github commit object.

        :param oauth_token: A valid OAuth token for authentication.
        :param repository: The full repository name.
        :param sha: The commit SHA.
        """
        self._token = oauth_token
        self._repository = repository
        self._sha = sha
        self._url = '/repos/' + repository + '/commits/' + sha
        self._data = get(self._token, self._url)

    @property
    def sha(self):
        """
        Retrieves the SHA of the commit:

        >>> from os import environ
        >>> commit = GitHubCommit(environ['GITHUB_TEST_TOKEN'],
        ...                       'gitmate-test-user/test', '674498')
        >>> commit.sha
        '674498fd415cfadc35c5eb28b8951e800f357c6f'

        :return: A string holding the full SHA of the commit.
        """
        return self._data['sha']

    @property
    def repository(self):
        """
        Retrieves the repository that holds this commit.

        >>> from os import environ
        >>> commit = GitHubCommit(environ['GITHUB_TEST_TOKEN'],
        ...                       'gitmate-test-user/test', '3fc4b86')
        >>> commit.repository.full_name
        'gitmate-test-user/test'

        :return: A usable Repository instance.
        """
        return GitHubRepository(self._token, self._repository)

    @property
    def parent(self):
        """
        Retrieves the parent commit. In case of a merge commit the first parent
        will be returned.

        >>> from os import environ
        >>> commit = GitHubCommit(environ['GITHUB_TEST_TOKEN'],
        ...                       'gitmate-test-user/test', '3fc4b86')
        >>> commit.parent.sha
        '674498fd415cfadc35c5eb28b8951e800f357c6f'

        :return: A Commit object.
        """
        return GitHubCommit(self._token, self._repository,
                            self._data['parents'][0]['sha'])

    def set_status(self, status: CommitStatus):
        """
        Adds the given status to the commit.

        >>> from os import environ
        >>> commit = GitHubCommit(environ['GITHUB_TEST_TOKEN'],
        ...                       'gitmate-test-user/test', '3fc4b86')
        >>> status = CommitStatus(Status.FAILED, 'Theres a problem',
        ...                       'gitmate/test')
        >>> commit.set_status(status)
        >>> commit.get_statuses().pop().description
        'Theres a problem'

        If a status with the same context already exists, it will be bluntly
        overridden:

        >>> status.status = Status.SUCCESS
        >>> status.description = "Theres no problem"
        >>> commit.set_status(status)
        >>> len(commit.get_statuses())
        2
        >>> commit.get_statuses().pop().description
        'This commit needs work.'

        :param status: The CommitStatus to set to this commit.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        data = {'state': GH_STATE_TRANSLATION[status.status],
                'target_url': status.url, 'description': status.description,
                'context': status.context}
        status_url = '/repos/' + self._repository + '/statuses/' + self.sha
        post(self._token, status_url, data)

    def get_statuses(self) -> {CommitStatus}:
        """
        Retrieves the all commit statuses.

        :return: A (frozen)set of CommitStatus objects.
        :raises RuntimeError: If something goes wrong (network, auth...).
        """
        url = self._url + '/statuses'
        statuses = get(self._token, url)

        # Only the first of each context is the one we want
        result = set()
        contexts = set()
        for status in statuses:
            if status['context'] not in contexts:
                result.add(CommitStatus(
                    INV_GH_STATE_TRANSLATION[status['state']],
                    status['description'], status['context'],
                    status['target_url']))
                contexts.add(status['context'])

        return result

    def get_patch_for_file(self, filename: str):
        r"""
        Retrieves the patch for the given file:

        >>> from os import environ
        >>> commit = GitHubCommit(environ['GITHUB_TEST_TOKEN'],
        ...                       'gitmate-test-user/test', '3fc4b86')
        >>> commit.get_patch_for_file('README.md')
        '@@ -1,2 +1,4 @@\n # test\n a test repo\n+\n+a tst pr'

        But only if it exists!

        >>> commit.get_patch_for_file('isnt there!')
        Traceback (most recent call last):
         ...
        IGitt.ElementDoesntExistError: The file does not exist.

        :param filename: The file to receive the patch for.
        :return: A string containing the patch.
        :raises ElementDoesntExistError: If the given filename doesn't exist.
        """
        for file in self._data['files']:
            if file['filename'] == filename and 'patch' in file:
                return file['patch']

        raise ElementDoesntExistError('The file does not exist.')

    def comment(self, message: str, file: (str, None)=None,
                line: (int, None)=None, mr_number: int=None):
        """
        Places a comment on the commit.

        >>> from os import environ
        >>> commit = GitHubCommit(environ['GITHUB_TEST_TOKEN'],
        ...                       'gitmate-test-user/test', '3fc4b86')

        So this line places a comment on the bottom of the commit,
        not associated to any particular piece of code:

        >>> commit.comment("An issue is here!")

        However, we can also comment on a particular file and line, if that is
        included in the diff:

        >>> commit.comment("Here in line 4, there's a spelling mistake!",
        ...                'README.md', 4)

        If you supply the ``pr_number`` argument, the comment will appear in the
        review UI of that pull request:

        >>> commit.comment("Here in line 4, there's a spelling mistake!",
        ...                'README.md', 4, mr_number=6)

        Beat that! Of course, there's a lot of error handling. If you give the
        wrong file, the comment will appear below the commit with a note about
        the commit, file and line:

        >>> commit.comment("Oh, this'll end up below!!", 'READMENOT.md', 4)

        Also if the line isn't contained in the diff GitHub won't accept that
        and it'll also end up below - sorry!

        >>> commit.comment("Oh, this'll too end up below!!", 'README.md', 8)

        If you give a pull request, the comment will appear on the PR instead:

        >>> commit.comment("Oh, this'll too end up on the PR.",
        ...                'README.md', 8, mr_number=6)

        :param message: The body of the comment.
        :param file: The file to place the comment, relative to repository root.
        :param line: The line in the file in the comment or None.
        :param mr_number: The number of a merge request if this should end up in
                          the review UI of the merge request.
        """
        data = {'body': message}

        if file is not None and line is not None:
            try:
                patch = self.get_patch_for_file(file)
                index = get_diff_index(patch, line)
                if index:  # Else, fallback to comment below file
                    data['position'] = index
                    data['path'] = file
            except ElementDoesntExistError:
                pass  # Fallback to comment below the file

        if 'position' not in data:
            file_str = "" if file is None else ", file " + file
            line_str = "" if line is None else ", line " + str(line)
            data['body'] = ("Comment on " + self.sha + file_str + line_str +
                            ".\n\n" + data['body'])

        if mr_number is None:
            post(self._token, self._url + '/comments', data)
        elif 'position' in data:
            data['commit_id'] = self.sha
            post(self._token,
                 '/repos/' + self._repository + "/pulls/" + str(mr_number) +
                 "/comments", data)
        else:  # Position not available, pr number available, comment on PR
            post(self._token,
                 '/repos/' + self._repository + "/issues/" + str(mr_number) +
                 "/comments", data)
