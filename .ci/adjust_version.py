#!/usr/bin/env python3

"""
A simple script to adjust a version number in a VERSION file.
"""

import argparse


def get_args():
    """
    Retrieves the arguments for the application using an argument parser.

    :return: The parser.parse_args() retval.
    """
    parser = argparse.ArgumentParser(
        description="This program allows rewriting a version file. It checks "
                    "if the new version is a valid successor of the existent "
                    "one and overwrites the version file accordingly.")
    parser.add_argument(dest="version_file", type=str)
    parser.add_argument("--build", "-b", type=int)
    parser.add_argument("--new-version", "-n", type=str)
    parser.add_argument("--release", "-r", action="store_true")
    args = parser.parse_args()
    if not args.release and args.build is None:
        parser.error("--build must be given for development versions.")

    return args


def get_valid_version(old_version_string, new_version_string):
    """
    Gets the split up version of the new_version_string if it is not None.

    :param old_version_string: The old version string.
    :param new_version_string: The new version string.
    :return: A tuple containing major, minor and micro version number.
    :raises AssertionError: If the new version is not a valid version jump.
    """
    old_version = old_version_string.split(".")
    old_major, old_minor, old_micro = map(int, old_version[:3])

    if new_version_string:
        new_version = new_version_string.split(".")
        assert len(new_version) == 3, ("A new version must consist of "
                                       "exactly 3 integers (e.g. 0.1.1).")
        new_major, new_minor, new_micro = map(int, new_version)
        jump_valid = ((new_major == old_major and
                       new_minor in (old_minor+1, old_minor)) or
                      (new_major == old_major+1 and new_minor == 0))
        assert jump_valid, "Invalid version jump."
        assert (((new_minor in (0, old_minor+1)) and new_micro == 0) or
                (new_minor == old_minor
                 and new_micro in (old_micro,
                                   old_micro+1))), "Invalid version jump."

        old_major, old_minor, old_micro = new_major, new_minor, new_micro

    return str(old_major), str(old_minor), str(old_micro)


def main():
    """
    The whole script!
    """
    args = get_args()

    with open(args.version_file, "r") as file:
        version_string = file.readline().strip()
    version = get_valid_version(version_string, args.new_version)

    version_string = ".".join(version)
    if not args.release:
        version_string += ".dev" + str(args.build)

    with open(args.version_file, "w") as file:
        file.write(version_string+"\n")


if __name__ == '__main__':
    main()
