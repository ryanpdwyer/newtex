# -*- coding: utf-8 -*-
"""
Key features:

Initialize the repository with:

.gitignore
NAME.tex
refs/
    MASTER_BIB_FILE.bib
styles/
    git submodule?, or just copy / pasted
figs/
    ex.png


Naming convention: Keep it short!
    YR[TYPE]_[INITIALS]_[SHORT TITLE]
"""
from __future__ import print_function, division, absolute_import

import io
import os
from os import path
import string
import datetime
import shutil
import pathlib
import distutils.dir_util
from fabric.api import local

import click
import yaml


def new_path(path_string):
    """Return pathlib.Path, expanding '~' to a user's HOME directory"""
    return pathlib.Path(path.expanduser(path_string))


def copy(src_path, dst_path):
    shutil.copy(str(src_path), str(dst_path))


def copy_tree(src_path, dst_path):
    """Recursively copy all files and folders from src_path to dst_path"""
    distutils.dir_util.copy_tree(str(src_path), str(dst_path))


def remove(path):
    """Remove the specified Path"""
    os.remove(str(path))

pkg_dir = new_path(path.dirname(__file__))

pkg_config_dir = pkg_dir/'newtexrc'

config_dir = new_path('~/newtex')

today = datetime.date.today()


default_config = u"""---
# newtex config file

created: {date}

# Uncomment and replace with the path to your default bib file
# master_bib_file: path/to/master_bib.bib

# Default bibliography style
# See contents of styles folder for available options
default_style: naturemag_jm.bst

# Uncomment and correct the authors and affiliations list
authors:
#    - Your Name
#    - John A. Marohn
# Please include an affiliation for each author
affiliations:
#    - Department of Chemistry and Chemical Biology, Ithaca NY 14853
#    - Department of Chemistry and Chemical Biology, Ithaca NY 14853
"""


def write_file(filename, string):
    io.open(str(filename), 'w', encoding="utf-8").write(string)


def no_config_dir(config_dir, config_file):
    """Create the config path if it doesn't exist."""

    click.confirm(
        'Setup config directory at {0}?'.format(str(config_dir)), abort=True)

    if not config_dir.exists():
        copy_tree(pkg_config_dir, config_dir)

    today = datetime.date.today().isoformat()

    write_file(str(config_file), default_config.format(date=today))

    click.echo('Please setup your config file\n{0}'.format(str(config_file)))
    click.edit(filename=str(config_file))
    raise click.Abort()


def check_config(config):
    expected_keys = {'master_bib_file', 'authors', 'affiliations',
                     'default_style'}
    for key, val in config.items():
        if val is None:
            raise click.ClickException(
                "The config parameter '{key}' must be specified.".format(
                    key=key))

    keys_okay = True
    for key in expected_keys:
        if key not in config:
            click.echo('{key} must be specified.'.format(key=key))
            keys_okay = False

    if not keys_okay:
        click.echo(
            "Please fix your config file before proceding")
        raise click.Abort()


@click.command(help="Create a new LaTeX document with references, etc")
@click.option('--type', default=None, help="Document type: FP GR GT etc")
@click.option('--folder-name', default=None, type=click.Path(file_okay=False),
              help="Document folder name; last folder is also doc filename (no spaces)")
@click.option('--title', default=None, help="Document title")
@click.option('--config-dir', default=config_dir)
def cli(folder_name, title, config_dir, type):

    # Configuration file setup, checking
    config_file = config_dir/'config.yaml'

    if not config_dir.exists() or not config_file.exists():
        no_config_dir(config_dir, config_file)

    config = yaml.load(io.open(str(config_file)))

    check_config(config)

    # Handle unset command line arguments
    if folder_name is None:
        folder_name = click.prompt('What should the folder be called?',
                                   type=click.Path(file_okay=False))

    if title is None:
        title = click.prompt("What is the document's title?")

    # Actual copying, renaming, inserting into template

    # Where to copy all of the files
    doc_dir = new_path(folder_name)

    if ' ' in doc_dir.name:
        raise click.ClickException("Name the folder without spaces")

    copy_tree(config_dir, doc_dir)

    remove(doc_dir/'config.yaml')

    (doc_dir/'gitignore').rename(doc_dir/'.gitignore')

    # Copy master bib file
    master_bib = new_path(config['master_bib_file'])

    copy(master_bib, doc_dir/'refs'/master_bib.name)

    tex_file = doc_dir/'template.tex'
    # Use the template to update the tex doc
    tex_template = string.Template(io.open(str(tex_file)).read())

    replaced_tex = tex_contents(tex_template, title=title,
        date=today, authors=config['authors'],
        affiliations=config['affiliations'],
        default_style=config['default_style'],
        default_bib=master_bib.name)

    write_file(tex_file, replaced_tex)

    tex_file.rename(doc_dir/(doc_dir.name+'.tex'))

    click.echo("""\
Your document is located in the directory:
{0}
You can now try compiling your document,
and 'git init' the repository""".format(str(doc_dir)))



def tex_contents(tex_template, title, date, authors, affiliations,
                 default_style, default_bib):
    main_author = authors[0]
    date_str = "{month} {d.day}, {d.year}".format(month=date.strftime("%B"),
                                                  d=date)

    author_affil_temp = string.Template(r"""
    \author{$author}
    \affiliation{$affiliation}""")

    author_affiliation_list = [
        author_affil_temp.substitute(author=author, affiliation=affiliation)
        for author, affiliation in zip(authors, affiliations)]

    author_affiliation_block = "\n".join(author_affiliation_list)

    return tex_template.substitute(
        title=title,
        main_author=main_author,
        date=date_str,
        author_affiliation_block=author_affiliation_block,
        default_style=default_style,
        default_bib=default_bib)


def test_tex_contents():
    title = "Example"
    date = datetime.date.today()
    authors = ["Ryan Dwyer", "John A. Marohn"]
    affiliations = [
        "Department of Chemistry and Chemical Biology, Ithaca NY 14853",
        "Department of Chemistry and Chemical Biology, Ithaca NY 14853"]

    default_style = "naturemag_jm.bst"
    default_bib = "jam99_2012-03-29_Ryan.bib"

    open('ex.tex', 'wb').write(
        tex_contents(title, date, authors, affiliations,
                     default_style, default_bib))


def create_bare_dropbox_repo(path, dropbox):
    """Takes an existing git repository at path, creates a corresponding bare
    Dropbox repository"""
    path = new_path(path).absolute()
    repository = path.name
    dropbox = new_path(dropbox).absolute()
    git_path = path/'.git'
    git_dropbox = dropbox/(repository+'.git')

    local("cd {dropbox} && git clone --bare {git_path}".format(
        dropbox=str(dropbox), git_path=str(git_path)))
    local("cd {path} && git remote add origin {git_dropbox} && git push -u origin master".format(path=str(path), git_dropbox=str(git_dropbox)))



from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
