# -*- coding: utf-8 -*-
import glob
import os
import shutil
import pathlib
from fabric.api import task


@task(default=True)
def copy():
    master_bib = pathlib.Path("$master_bib")
    dest = pathlib.Path('bib')/master_bib.name
    shutil.copyfile(str(master_bib.absolute()), str(dest))


@task
def help():
    print("""\
Commands:

    copy            copy bib file to refs [default]
    clean           remove latex intermediate files""")


@task
def clean():
    globs = [
            '*.aux',
            '*.bak',
            '*.bbl',
            '*.blg',
            '*.dvi',
            '*.fgx',
            '*.log',
            '*.out',
            '*.pdf',
            '*.synctex.gz',
            '*.sav',
            '*.spl',
            '*.tbx',
            '*.vdx',
            '*.fdb_latexmk',
            '*.fls',
            '*.mp',
            '*.top',
            '*.tui']
    to_remove = []

    for glob_pattern in globs:
        to_remove.extend(glob.glob(glob_pattern))

    for filename in to_remove:
        os.remove(filename)
