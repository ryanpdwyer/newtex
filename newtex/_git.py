# -*- coding: utf-8 -*-
import sys
import os
import click
from fabric.api import local


class cd:
    """Context manager for changing the current working directory.

    From http://stackoverflow.com/a/13197763"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


if sys.platform == 'Windows':
    shell = local('where powershell', capture=True)
else:
    shell = None



def parse_git_config(raw_config):
    """Return a dict for a string containing git conig --list output"""
    return dict([line.split('=') for line in raw_config.split('\n')])


def check_git():
    """Check to see that you have git on your path, and that your email and
    username are correctly configured."""

    version = local("git --version", capture=True, shell=shell)
    if 'version' not in version:
        raise click.ClickException(
            """\
git is not on your PATH; on Windows, try running from Git Bash, or
reinstalling git and selecting 'Use Git from the Windows Command Prompt'
if you'd prefer to use PowerShell.""")
    raw_config = local("""git config --list""", capture=True, shell=shell)
    dict_config = parse_git_config(raw_config)

    if 'user.name' not in dict_config or 'user.email' not in dict_config:
        raise click.ClickException("""
Please set up your name and email address in git by running,

    git config --global user.name "YOUR NAME"
    git config --global user.email "YOUR EMAIL"
""")


def inital_git_commit(path):
    path_string = str(path.absolute())
    print("cd {0}".format(path_string))
    with cd(path_string):
        local("git init", shell=shell)
        local("git add -A", shell=shell)
        local('git commit -m "Initial automatic commit by newtex"', shell=shell)


def create_bare_repo(path, bare_path):
    """Takes an existing git repository at path, creates a corresponding bare
    repository at bare_path """
    repository = path.name
    git_path = path.absolute()/'.git'
    git_bare_path = bare_path/(repository+'.git')

    bare_path_string = str(bare_path.absolute())

    print("cd {0}".format(bare_path_string))
    with cd(bare_path_string):
        local('git clone --bare "{git_path}"'.format(
            git_path=str(git_path.absolute())), shell=shell)

    path_string = str(path.absolute())
    print("cd {0}".format(path_string))
    with cd(path_string):
        local('git remote add origin "{git_bare_path}"'.format(
            git_bare_path=str(git_bare_path.absolute())), shell=shell)
        local("git push -u origin master", shell=shell)
