"""Command-line interface for PyBryt"""

import dill
import click

from .reference import ReferenceImplementation

@click.group()
def main():
    pass

@main.command("compile")
@click.argument("src", type=click.Path(exists=True))
@click.argument("dest", type=click.Path(), default="reference.pkl")
def compile_reference(src, dest):
    refs = ReferenceImplementation.compile(src)
    with open(dest, "wb+") as f:
        dill.dump(refs, f)
