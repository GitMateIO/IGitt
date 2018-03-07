#!/usr/bin/env python3

"""
Provides a main routine that can install IGitt and create distributions.
"""
from setuptools import find_packages, setup

from IGitt import VERSION

with open('requirements.txt') as requirements:
    REQUIRED = requirements.read().splitlines()


if __name__ == '__main__':
    setup(name='IGitt',
          version=VERSION,
          description='A git(hub/lab/...) hosting abstraction library.',
          author='Lasse Schuirmann',
          maintainer='Lasse Schuirmann',
          maintainer_email='lasse.schuirmann@gmail.com',
          packages=find_packages(exclude=['build.*', '*.tests.*', '*.tests']),
          install_requires=REQUIRED,
          package_data={'IGitt': ['VERSION']},
          license='MIT')
