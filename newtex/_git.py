# -*- coding: utf-8 -*-
import click
from fabric.api import local, lcd


def parse_git_config(raw_config):
    """Return a dict for a string containing git conig --list output"""
    return dict([line.split('=') for line in raw_config.split('\n')])


def check_git():
    """Check to see that you have git on your path, and that your email and
    username are correctly configured."""

    version = local("git --version", capture=True)
    if 'version' not in version:
        raise click.ClickException(
            """\
git is not on your PATH; on Windows, try running from Git Bash, or
reinstalling git and selecting 'Use Git from the Windows Command Prompt'
if you'd prefer to use PowerShell.""")
    raw_config = local("""git config --list""", capture=True)
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
    with lcd(path_string):
        local("git init")
        local("git add -A")
        local("git commit -m 'Initial automatic commit by newtex'")

def create_bare_repo(path, bare_path):
    """Takes an existing git repository at path, creates a corresponding bare
    repository at bare_path """
    repository = path.name
    git_path = path/'.git'
    git_bare_path = bare_path/(repository+'.git')

    bare_path_string = str(bare_path.absolute())

    print("cd {0}".format(bare_path_string))
    with lcd(bare_path_string):
        local("git clone --bare {git_path}".format(
            git_path=str(git_path.absolute())
        ))

    path_string = str(path.absolute())
    print("cd {0}".format(path_string))
    with lcd(path_string):
        local("git remote add origin {git_bare_path}".format(
            git_bare_path=str(git_bare_path.absolute())
        ))
        local("git push -u origin master")
