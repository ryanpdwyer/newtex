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
import ntpath
import distutils.dir_util


import click
import yaml

pkg_dir = path.dirname(__file__)

pkg_config_dir = path.join(pkg_dir, 'newtexrc')

config_dir = path.expanduser('~/newtex')

today = datetime.date.today()


def new_path(path_string):
    return pathlib.Path(path.expanduser(path_string))


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
    io.open(filename, 'w', encoding="utf-8").write(string)


def no_config_dir(config_dir, config_file):
    """Create the config path if it doesn't exist."""
    click.confirm('Setup config directory at ~/newtex?', abort=True)

    if not path.exists(config_dir):
        distutils.dir_util.copy_tree(pkg_config_dir, config_dir)

    today = datetime.date.today().isoformat()

    write_file(config_file, default_config.format(date=today))

    click.echo('Please setup your config file (~/newtex/config.yaml)')
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


@click.command()
@click.option('--folder-name', prompt='What should the folder be called?', type=click.Path(file_okay=False))
@click.option('--title', prompt="What is the document's title?")
def cli(folder_name, title):
    config_file = path.join(config_dir, 'config.yaml')

    if not path.exists(config_dir) or not path.exists(config_file):
        no_config_dir(config_dir, config_file)

    config = yaml.load(io.open(config_file))

    check_config(config)

    # Where to copy all of the files
    doc_dir = path.abspath(folder_name)

    distutils.dir_util.copy_tree(config_dir, doc_dir)

    os.rename(path.join(doc_dir, 'gitignore'),
              path.join(doc_dir, '.gitignore'))

    # Copy master bib file
    master_bib_path = path.abspath(config['master_bib_file'])
    click.echo(master_bib_path)
    master_bib_filename = ntpath.basename(master_bib_path)
    shutil.copy(master_bib_path,
                path.normpath(path.join(doc_dir, 'refs/', master_bib_filename)))


    tex_file = path.join(doc_dir, 'template.tex')
    # Use the template to update the tex doc
    tex_template = string.Template(io.open(tex_file).read())

    replaced_tex = tex_contents(tex_template, title=title,
        date=today, authors=config['authors'],
        affiliations=config['affiliations'],
        default_style=config['default_style'],
        default_bib=master_bib_filename)

    write_file(tex_file, replaced_tex)

    click.echo("Folder name:  {folder_name}".format(folder_name=folder_name))
    click.echo("Title      :  {title}".format(title=title))


def tex_contents(tex_template, title, date, authors, affiliations,
                 default_style, default_bib):
    main_author = authors[0]
    date_str = "{month} {d.day}, {d.year}".format(month=date.strftime("%B"),
                                                   d=date)

    author_affil_temp = string.Template(r"""\
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

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
