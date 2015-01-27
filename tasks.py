# Invoke tasks file
# Python 2/3 Makefile replacement
# To do:
#   - Add commands to build docs
# Dependencies:
# six, packaging, pathlib, invoke
# Python2 (optional): subprocess32

import os
import shutil

import pathlib
import packaging.version
from six.moves import input
from invoke import task, run

cwd = pathlib.Path('.')


# Helper functions for unix-like removing folders and files.
def rm_rf(*args):
    """Recursively delete directories, if they exist"""
    for directory in args:
        try:
            shutil.rmtree(str(directory))
        except OSError:
            pass


def rm(*args):
    """Delete all files provided"""
    for path in args:
        try:
            os.remove(str(args))
        except OSError:
            pass


# Helper functions for getting version numbers
def git_describe():
    result = run('git describe --tags --dirty --always')
    return result.stdout


def version():
    result = run('python setup.py --version')
    return result.stdout


@task(default=True)
def help():
    print("""
Usage:  inv[oke] [--core-opts] task1 [--task1-opts] ... taskN [--taskN-opts]

Tasks:

clean           Remove compiled python files, build directories
test            Run tests for package (python setup.py test)
release         Upload to PyPI after running tests and checking version number

To see more about a specific task, run invoke --help task""")


@task
def clean():
    """Remove build directories, compiled python files"""
    rm_rf('dist')
    rm(*cwd.rglob("*.py[cod]"))

    rm_rf('build', '__pycache__')

    rm_rf(*cwd.glob('*.egg'))
    rm_rf(*cwd.glob('*.egg-info'))


@task
def test():
    """Test the package using python setup.py test"""
    run('python setup.py test')


@task
def check_version():
    """Raise an error if the version number is not PEP440 compatible"""
    packaging.version.Version(version())
    print("Version okay.")


@task
def check_version_tag():
    """Before releasing, check that the version matches the git tag"""
    git_describe_version = git_describe()
    setuppy_version = version()
    if setuppy_version == git_describe_version:
        print("Versions match.")
    elif 'dirty' in git_describe_version:
        raise ValueError("""Working directory has uncommited changes.\
            Commit before releasing.""")
    else:
        choice = input("Release without tagging\n(version {0})? [y/N]\n".format(
            setuppy_version)).lower()
        if choice[0] == 'y':
            print("Continuing")
        else:
            raise ValueError("Stopping.")


@task(clean, test, check_version, check_version_tag)
def release():
    """Check that tests pass, the version is correct, then build source, wheel
    distributions, upload to PyPI using twine."""
    run('python setup.py sdist bdist_wheel')
    run('twine upload dist/*')
