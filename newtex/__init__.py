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
import string
import datetime
import shutil
import pathlib
import distutils.dir_util

import click
import yaml

from newtex._git import check_git, inital_git_commit, create_bare_repo

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def new_path(path_string):
    """Return pathlib.Path, expanding '~' to a user's HOME directory"""
    return pathlib.Path(os.path.expanduser(path_string))


def copy(src_path, dst_path):
    shutil.copy(str(src_path), str(dst_path))


def copy_tree(src_path, dst_path):
    """Recursively copy all files and folders from src_path to dst_path"""
    distutils.dir_util.copy_tree(str(src_path), str(dst_path))


def mkdir(path):
    os.mkdir(str(path))


def remove(path):
    """Remove the specified path"""
    os.remove(str(path))


def read_file(filename):
    return io.open(str(filename)).read()


def write_file(filename, string):
    io.open(str(filename), 'w', encoding="utf-8").write(string)


pkg_dir = new_path(os.path.dirname(__file__))

pkg_config_dir = pkg_dir/'newtexrc'

today = datetime.date.today()


default_config = u"""---
# newtex config file

created: {date}

# Uncomment and replace with the path to your default bib file
# Make sure to put the path in single quotes on windows

#master_bib_file: 'path/to/master_bib.bib'

# Default bibliography style
# See contents of styles folder for available options

default_style: naturemag_jm.bst

# Uncomment and correct the authors and affiliations list
# Please include an affiliation for each author
authors:
#    - Your Name
#    - John A. Marohn
affiliations:
#    - Department of Chemistry and Chemical Biology, Ithaca, New York 14853
#    - Department of Chemistry and Chemical Biology, Ithaca, New York 14853

# Dropbox path
# Only necessary if your Dropbox is in a non-standard location

#dropbox: 'path/to/dropbox'
"""


def no_config_dir(config_dir, config_file):
    """Create the config path if it doesn't exist."""

    click.confirm(
        'Setup config directory at {0}?'.format(str(config_dir)), abort=True)

    if not config_dir.exists():
        copy_tree(pkg_config_dir, config_dir)

    today = datetime.date.today().isoformat()

    write_file(str(config_file), default_config.format(date=today))

    click.echo('Please setup your config file\n{0}'.format(str(config_file)))
    click.launch(str(config_file))
    raise click.Abort()


def verify_config(config):
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


def dir_doc_names(doc_type, last_name, date, short_name):
    """Return properly formatted directory and document names"""
    yrmonth = date.strftime("%Y%m")
    dir_name = (
        "_JAM_{doc_type}__{last_name}{yrmonth}__{short_name}".format(
            doc_type=doc_type,
            last_name=last_name,
            yrmonth=yrmonth,
            short_name=short_name))

    doc_name = "{last_name}{yrmonth}__{short_name}.tex".format(
        last_name=last_name,
        yrmonth=yrmonth,
        short_name=short_name)

    return dir_name, doc_name


doc_type_choices = click.Choice(['FP', 'GR', 'GT', 'RP', 'MS'])


def print_version(ctx, param, value):
    """Print newtex version at command line.
    See http://click.pocoo.org/3/options/#callbacks-and-eager-options"""
    if not value or ctx.resilient_parsing:
        return
    click.echo("newtex version {0}".format(__version__))
    ctx.exit()

default_config_dir = '~/newtex_template'

def reconfigure(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    config_dir = default_config_dir

    # Configuration file setup
    config_dir = new_path(config_dir)
    config_file = config_dir/'config.yaml'

    click.confirm(
        'Reconfigure config directory at {0}?'.format(str(config_dir)), abort=True)

    copy_tree(pkg_config_dir, config_dir)

    ctx.exit()


@click.command(help="Create a new LaTeX document with references, etc")
@click.option('--doc-type', default=None,
              help="Document type: FP GR GT etc",
              type=doc_type_choices)
@click.option('--destination', default='.', type=click.Path(file_okay=False))
@click.option('--short-name', default=None, type=click.Path(file_okay=False),
              help="Short name for document")
@click.option('--title', default=None, help="Document title")
@click.option('--config-dir', default=default_config_dir,
              type=click.Path(file_okay=False))
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Print newtex version")
@click.option('--reconfigure', is_flag=True, callback=reconfigure,
              expose_value=False, is_eager=True,
              help="Setup config folder again")
def cli(short_name, title, config_dir, doc_type, destination):

    # Configuration file setup
    config_dir = new_path(config_dir)
    config_file = config_dir/'config.yaml'

    if not config_dir.exists() or not config_file.exists():
        no_config_dir(config_dir, config_file)

    config = yaml.load(read_file(config_file))

    verify_config(config)

    last_name = config['authors'][0].split(' ')[-1]

    check_git()

    # Handle unset command line arguments
    if short_name is None:
        short_name = click.prompt('Short name for document (2-3 words)?')

    short_name = short_name.replace(' ', '_').replace('-', '_')

    if title is None:
        title = click.prompt("What is the document's title?")

    if doc_type is None:
        doc_type = click.prompt("""
    FP: Flight Plan
    MS: Manuscript
    GT: Grant
    GR: Grant Report
    RP: Report

What type is the document? [FP, MS, GT, GR, RP]""", type=doc_type_choices)

    # Actual copying, renaming, inserting into template

    dir_name, doc_name = dir_doc_names(doc_type, last_name, today, short_name)

    # Where to copy all of the files
    destination_dir = new_path(destination)
    doc_dir = destination_dir/dir_name

    if ' ' in doc_dir.name:
        raise click.ClickException("Name the folder without spaces")

    copy_tree(config_dir, doc_dir)

    remove(doc_dir/'config.yaml')

    (doc_dir/'gitignore').rename(doc_dir/'.gitignore')

    # Copy master bib file
    master_bib = new_path(config['master_bib_file'])

    copy(master_bib, doc_dir/'bib'/master_bib.name)

    fabfile_template = string.Template(read_file(doc_dir/'fabfile.py'))

    write_file(doc_dir/'fabfile.py', fabfile_template.substitute(
        master_bib=str(master_bib.absolute()),
        master_bib_name=master_bib.name))

    dropbox = new_path(config.get('dropbox', '~/Dropbox'))
    large_figs_dir = (dropbox/(doc_dir.name+'__figs')).absolute()

    tex_file = doc_dir/'template.tex'
    tex_template = string.Template(read_file(tex_file))
    replaced_tex = tex_contents(tex_template, title=title,
                                date=today, authors=config['authors'],
                                affiliations=config['affiliations'],
                                default_style=new_path(config['default_style']).stem,
                                default_bib=master_bib.stem,
                                large_figs_dir=str(large_figs_dir))

    write_file(tex_file, replaced_tex)

    tex_file.rename(doc_dir/doc_name)

    inital_git_commit(doc_dir)
    create_bare_repo(doc_dir, dropbox)
    mkdir(large_figs_dir)

    bare_repo = str(dropbox/(dir_name+'.git'))

    click.echo("""
To collaborate with others on this document, share the Dropbox folders,

    {bare_repo}
    {large_figs_dir}

To work on this document, go to:

    {doc_dir}

You should be able to make changes and do:

git commit -a -m "Message"
git pull    [this will pull from the dropbox bare repository]
git push    [this will push to the dropbox bare repository]
""".format(
        bare_repo=bare_repo,
        large_figs_dir=str(large_figs_dir),
        doc_dir=str(doc_dir)))

    click.launch(bare_repo, locate=True)


def tex_contents(tex_template, title, date, authors, affiliations,
                 default_style, default_bib, large_figs_dir):
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
        default_bib=default_bib,
        large_figs_dir=large_figs_dir+'/')


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

