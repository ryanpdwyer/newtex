# -*- coding: utf-8 -*-
import glob
import os
from fabric.api import local


def help():
    print("cpbib        copy bib file to refs")
    print("clean        remove latex intermediate files")


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
        to_remove.append(glob.glob(glob_pattern))

    for filename in to_remove:
        os.remove(filename)
