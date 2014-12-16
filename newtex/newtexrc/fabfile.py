# -*- coding: utf-8 -*-
import glob
import os
import shutil
from fabric.api import task


@task(default=True)
def copy():
    master_bib = "$master_bib"
    dest = "bib/$master_bib_name"
    shutil.copyfile(master_bib, dest)
    print("Copied {0}".format(master_bib))


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
            '*.tui',
            '*.pyc']
    to_remove = []

    for glob_pattern in globs:
        to_remove.extend(glob.glob(glob_pattern))

    for filename in to_remove:
        os.remove(filename)

    print("Removed aux / compiled files")
