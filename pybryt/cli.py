"""Command-line interface for PyBryt"""

import os
import json
import click

from . import generate_student_impls, ReferenceImplementation, StudentImplementation
from .utils import get_stem


@click.group()
def click_cli():
    """
    A command-line interface for PyBryt. See https://microsoft.github.io/pybryt for more information.
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


@click_cli.command()
@click.option("-n", "--name", default=None, type=click.STRING, 
              help="Optional name for the reference implementation")
@click.option("--output-nb", default=None, type=click.Path(dir_okay=False), 
              help="Path at which to write the output notebook from executing the student submission")
@click.option("-o", "--output", default=None, type=click.Path(dir_okay=False), 
              help="Path at which to write the results of the check")
@click.option("-t", "--type", "output_type", default="pickle", show_default=True, 
              type=click.Choice(["pickle", "json"]), help="Type of output file to write")
@click.argument("ref", type=click.Path(exists=True, dir_okay=False))
@click.argument("stu", type=click.Path(exists=True, dir_okay=False))
def check(ref, stu, name, output_nb, output, output_type):
    """
    Runs the student notebook STU against the reference implementation REF. REF can be a path to a
    pickled reference implementation or to a notebook to be compiled on-the-fly.
    """
    if os.path.splitext(ref)[1] == ".ipynb":
        ref = ReferenceImplementation.compile(ref)
        if not isinstance(ref, ReferenceImplementation):
            raise RuntimeError("On-the-fly reference compilation must result in a single reference "
                               "implementation")
    else:
        try:
            ref = ReferenceImplementation.load(ref)
        except:
            raise RuntimeError(f"Could not load the reference implementation {ref}")

    stu = StudentImplementation(stu, output=output_nb)
    res = stu.check(ref)

    if output_type == "pickle":
        res.dump(output)
    elif output_type == "json":
        if output is None:
            output = os.path.splitext(res._default_dump_dest)[0] + ".json"
        d = res.to_dict()
        with open(output, "w+") as f:
            json.dump(d, f, indent=2)


@click_cli.command()
@click.option("-p", "--parallel/--no-parallel", default=False, show_default=True)
@click.option("-o", "--output", default=None, type=click.Path(), 
              help="Path at which to write the pickled student implementation")
@click.argument("subm", nargs=-1, type=click.Path(exists=True, dir_okay=False))
def execute(subm, parallel, output):
    """
    """
    stus = generate_student_impls(subm, parallel=parallel)

    if len(subm) == 1:
        stus[0].dump(output)
    else:
        if output is None:
            output = "./"
        if not os.path.isdir(output):
            raise ValueError(f"output directory {output} does not exist or is not a directory")

        for s, stu in zip(subm, stus):
            stem = get_stem(s)
            path = os.path.join(output, stem + ".pkl")
            stu.dump(path)


def cli(*args, **kwargs):
    """
    Wrapper for the click CLI that sets the prog name.
    """
    prog_name = kwargs.pop("prog_name", "pybryt")
    return click_cli(*args, prog_name=prog_name, **kwargs)
