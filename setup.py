#!/usr/bin/env python3

"""
Provides a main routine that can install IGitt and create distributions.
"""
from subprocess import call
import sys

import setuptools.command.build_py
from setuptools import find_packages, setup

from IGitt import VERSION


class BuildDocsCommand(setuptools.command.build_py.build_py):
    """
    Automatically generates the documentation with sphinx.
    """
    apidoc_command = (
        'sphinx-apidoc', '-f', '-o', 'docs', '--no-toc', 'IGitt'
    )
    doc_command = ('make', '-C', 'docs', 'html', 'SPHINXOPTS=-W')

    def run(self):
        errOne = call(self.apidoc_command)
        errTwo = call(self.doc_command)
        sys.exit(errOne or errTwo)


with open('requirements.txt') as requirements:
    REQUIRED = requirements.read().splitlines()

with open('README.rst') as readme:
    long_description = readme.read()


if __name__ == '__main__':
    setup(name='IGitt',
          cmdclass={'docs': BuildDocsCommand},
          version=VERSION,
          description='A git(hub/lab/...) hosting abstraction library.',
          long_description=long_description,
          url='https://gitlab.com/gitmate/open-source/IGitt/',
          author='Lasse Schuirmann',
          maintainer='Lasse Schuirmann',
          maintainer_email='lasse@gitmate.io',
          packages=find_packages(exclude=['build.*', '*.tests.*', '*.tests']),
          install_requires=REQUIRED,
          package_data={'IGitt': ['VERSION']},
          license='MIT')
