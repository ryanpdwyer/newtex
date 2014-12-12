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



master_bib_file: PATH

authors:
    - Ryan P. Dwyer
    - John A. Marohn
affiliations:
    - Department of Chemistry and Chemical Biology, Ithaca NY 14853
    - Department of Chemistry and Chemical Biology, Ithaca NY 14853



"""
from __future__ import print_function, division, absolute_import

import os
import string
import datetime


import click
import yaml

RC_PATH = os.path.expanduser('~/.newtex.yaml')


@click.command()
def cli():
    if not os.path.exists(RC_PATH):
        click.confirm('Setup configuration file?', abort=True)
    click.echo("Hello, World!")


def configure():
    pass


tex_file_template = string.Template(r"""%  $title
%  Created by $main_author $date

% %%   PREAMBLE   %%%

% PREPRINT
%\RequirePackage[displaymath,mathlines]{lineno}  % implement numbered lines
%\documentclass[aps,prl,preprint,citeautoscript,superscriptaddress,byrevtex,nofootinbib]{revtex4}
%\documentclass[aps,prl,preprint,citeautoscript,superscriptaddress,endfloats*,byrevtex,nofootinbib]{revtex4}

% GALLEY
%\RequirePackage[displaymath,mathlines]{lineno}  % implement numbered lines -- pagewise for two-column mode
%\documentclass[10pt,aps,prl,twocolumn,galley,citeautoscript,superscriptaddress,byrevtex,nofootinbib,nobalancelastpage,floatfix]{revtex4}

% TWO COLUMN
%\RequirePackage[displaymath,mathlines,pagewise]{lineno}  % implement numbered lines -- pagewise for two-column mode
%\RequirePackage[displaymath,mathlines]{lineno}  % implement numbered lines -- pagewise for two-column mode
\documentclass[aps,prl,twocolumn,citeautoscript,superscriptaddress,byrevtex,nofootinbib,nobalancelastpage,floatfix]{revtex4}

% PACKAGES
\usepackage{siunitx}    % package for \meter etc
\usepackage[pdftex]{graphicx}         % \includegraphics{}
\usepackage{fancyhdr}                 % \pagestyle{fancy}, \rhear{}, rfoo{}
\usepackage{amsmath}                  % \pmatrix{}, etc...
\usepackage{bm}                       % need for bold greek letters
\usepackage[letterpaper,
    margin=1.0in,
    includehead,
    includefoot,
    headsep=11pt]{geometry}   % large margins
\usepackage[colorlinks=true,
    citecolor=blue,
    linkcolor=blue,
    urlcolor=blue,
    pagebackref=false]{hyperref}
\usepackage{mciteplus}
\usepackage{bm}         % bold math
\usepackage{natbib}  % bibliography
%\RequirePackage{lineno}
                                    
% FONTS

% Computer Modern is the default LaTeX font.
% Uncomment one of the lines below to try another font.
% PRL actually appears to use a font closet to Times.
% \usepackage{times}     % ~not~ computer modern fonts
\usepackage{palatino}  % ~not~ computer modern fonts

% FORMATTING OPTIONS

\lefthyphenmin=3           % Fix LaTeX hyphenation
\righthyphenmin=4          % Fix LaTeX hyphenation
%\setlength{\parskip}{6pt}  % Set paragraph spacing to be easy on the eyes



% COMMANDS
\newcommand{\figloc}[1]{./figs/#1}   % Define subdirectory for figs
\newcommand{\bibloc}[1]{./refs/#1}   % Define subdirectory for bib figures
\newcommand{\trimcaptionspacing}{\vspace{-0.25in}}      % include in figures to decrease the text-to-figure spacing
\newcommand{\trimcaptionspacinghalf}{\vspace{-0.10in}}  % include in figures to decrease the text-to-figure spacing         
\def\bibfont{\footnotesize} % Smaller font in the bibliography

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%  Begin Document %%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\begin{document}

    \pagestyle{fancy}

        \lhead{\footnotesize \textsf{AUTHORS}}
        \chead{\normalsize Short title}
        \rhead{\footnotesize \textsf{\today}}
        \lfoot{}
        \cfoot{\thepage}
        \rfoot{}


    \title{$title}
$author_affiliation_block

    % LINE NUMBERING
    %\setpagewiselinenumbers
    %\modulolinenumbers[5]
    %\linenumbers

\begin{abstract}
    This is the abstract.
\end{abstract}

\date{\today}

\maketitle
\thispagestyle{fancy}


\section{Introduction}
This is the body.


% =========================
\def\bibsection{\vspace{6pt}}
\setlength{\bibsep}{0pt}

\bibliographystyle{styles/$default_style}

\bibliography{refs/$default_bib}
\label{TheEnd}
\end{document}
""")

author_affil_temp = string.Template(r"""\
    \author{$author}
    \affiliation{$affiliation}""")


gitignore = """
# IGNORE LATEX WORKING FILES

*.aux
*.bak
*.bbl
*.blg
*.dvi
*.fgx
*.log
*.out
*.pdf
*.synctex.gz
*.sav
*.spl
*.tbx
*.vdx

# IGNORE Latexmk
*.fdb_latexmk
*.fls


*.mp
*.top
*.tui

# IGNORE MATLAB data and MATHEMATICA and ADOBE ILLUDSTRATOR

# ignore matlab temp asv backup files
**.asv
# ignore matlab temporary backup files
**.m~
# ignore matlab binary data
**.mat
# ignore Mathematica notebook files ...
**.nb
# ignore Adobe Illustrator
**.ai

# IGNORE MS WORD

**.doc

# ANNOYING FILES

# A hidden file created by the Mac OS X Finder.
**.DS_Store
# Another annoying hidden file
**.dropbox
# Another annoying file
Icon?
# Ignore shortcuts
**.lnk
"""


def tex_contents(title, date, authors, affiliations,
                 default_style, default_bib):
    main_author = authors[0]
    date_str = "{month} {d.day}, {d.year}".format(month=date.strftime("%B"),
                                                  d=date)
    author_affiliation_list = [
        author_affil_temp.substitute(author=author, affiliation=affiliation)
        for author, affiliation in zip(authors, affiliations)]

    author_affiliation_block = "\n".join(author_affiliation_list)

    return tex_file_template.substitute(
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
