# -*- coding: utf-8 -*-
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import click


@click.command()
def cli():
    click.echo("Hello, World!")

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
