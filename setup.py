#!/usr/bin/env python

import os
import sys

from setuptools import setup

# See https://github.com/warner/python-versioneer
import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'newtex/_version.py'
versioneer.versionfile_build = 'newtex/_version.py'
versioneer.tag_prefix = '' # tags are like 1.2.0
versioneer.parentdir_prefix = 'newtex-' # dirname like 'myproject-1.2.0'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='newtex',
    version=versioneer.get_version(),
    description="Create a new LaTeX document.",
    author="Ryan Dwyer",
    author_email='ryanpdwyer@gmail.com',
    url='https://github.com/ryanpdwyer/newtex',
    packages=['newtex'],
    include_package_data=True,
    install_requires=['click', 'PyYAML'],
    tests_require=['nose>=1.0'],
    test_suite='nose.collector',
    license='MIT',
    zip_safe=False,
    cmdclass=versioneer.get_cmdclass(),
    entry_points="""
        [console_scripts]
        newtex=newtex:cli
    """,)
