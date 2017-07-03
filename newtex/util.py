# -*- coding: utf-8 -*-
import pathlib


# Use subprocess32 if available
try:
    import subprocess32 as subprocess
except:
    import subprocess as subprocess


cwd = pathlib.Path('.')


def check_output(*args, **kwargs):
    """Subprocess check_output, but prints commands and output by default.
    Also allows printing of error message for helpful debugging.

    Use print_all=False to turn off all printing."""
    print_all = kwargs.pop('print_all', None)
    if print_all is not None:
        print_in = print_all
        print_out = print_all
    else:
        print_in = kwargs.pop('print_in', True)
        print_out = kwargs.pop('print_out', True)

    if print_in:
        print('')
        print(' '.join(args[0]))

    try:
        out_bytes = subprocess.check_output(*args, **kwargs)
        out_lines = out_bytes.decode('utf-8').splitlines()
    except subprocess.CalledProcessError as e:
        # Wrap in try/except so that check_output can print
        raise e

    if print_out:
        for line in out_lines:
            print(line)

    return out_lines