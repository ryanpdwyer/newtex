#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    import platform
    print("""\
You do not have setuptools installed.

Python Information

    Version: {0}
    Path:    {1}

Install setuptools using,

    pip install setuptools

or see https://pypi.python.org/pypi/setuptools

""".format(platform.python_version(), sys.executable))
    raise


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
    setup_requires=["setuptools_git >= 0.3"],
    include_package_data=True,
    install_requires=['click', 'PyYAML', 'pathlib', 'fabric'],
    tests_require=['nose>=1.0'],
    test_suite='nose.collector',
    license='MIT',
    zip_safe=False,
    cmdclass=versioneer.get_cmdclass(),
    entry_points="""
        [console_scripts]
        newtex=newtex:cli
    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'],)
