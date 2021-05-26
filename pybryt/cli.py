"""Command-line interface for PyBryt"""

import click

from . import ReferenceImplementation


@click.group()
def click_cli():
    """
    """
    pass


@click_cli.command()
@click.option("-d", "--dest", default=None, type=click.Path(dir_okay=False), 
              help="Path at which to write the pickled reference implementation")
@click.option("-n", "--name", default=None, type=click.STRING, 
              help="Optional name for the reference implementation")
@click.argument("src", type=click.Path(exists=True, dir_okay=False))
def compile(src, dest, name):
    """
    Compile the reference implementation SRC.
    """
    ref = ReferenceImplementation.compile(src, name=name)
    ref.dump(dest)


def cli(*args, **kwargs):
    """
    """
    prog_name = kwargs.pop("prog_name", "pybryt")
    return click_cli(*args, prog_name=prog_name, **kwargs)
