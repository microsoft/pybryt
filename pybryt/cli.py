"""Command-line interface for PyBryt"""

import os
import dill
import json
import click

from . import (
    generate_report, generate_student_impls, ReferenceImplementation, StudentImplementation, __version__
)
from .utils import get_stem


@click.group()
@click.version_option(__version__)
def click_cli():
    """
    A command-line interface for PyBryt. See https://microsoft.github.io/pybryt for more information.
    """
    pass


@click_cli.command("compile")
@click.option("-d", "--dest", default=None, type=click.Path(dir_okay=False), 
              help="Path at which to write the pickled reference implementation")
@click.option("-n", "--name", default=None, type=click.STRING, 
              help="Optional name for the reference implementation")
@click.argument("src", type=click.Path(exists=True, dir_okay=False))
def compile_reference(src, dest, name):
    """
    Compile the reference implementation SRC.

    SRC must be a path to a Jupyter Notebook file which defines a reference implementation.
    """
    ref = ReferenceImplementation.compile(src, name=name)
    ref.dump(dest)


@click_cli.command()
@click.option("--output", default=None, type=click.Path(dir_okay=False), 
              help="Path at which to write the output notebook from executing the student submission")
@click.option("-d", "--dest", default=None, type=click.Path(dir_okay=False), 
              help="Path at which to write the results of the check")
@click.option("-t", "--type", "output_type", default="pickle", show_default=True, 
              type=click.Choice(["pickle", "json", "report"]), help="Type of output to write")
@click.argument("ref", type=click.Path(exists=True, dir_okay=False))
@click.argument("stu", type=click.Path(exists=True, dir_okay=False))
def check(ref, stu, output, dest, output_type):
    """
    Run a student submission against a reference implementation.

    REF can be a path to a pickled reference implementation or to a notebook to be compiled on-the-fly.
    STU can be a path to a pickled student implementation or to a notebook to be executed.

    If TYPE is "pickle" or "json", the output is a file. If TYPE is "report", a report is echoed to
    the console and OUTPUT is ignored.
    """
    if os.path.splitext(ref)[1] == ".ipynb":
        ref = ReferenceImplementation.compile(ref)
    else:
        try:
            ref = ReferenceImplementation.load(ref)
        except:
            raise RuntimeError(f"Could not load the reference implementation {ref}")

    if dest is None:
        dest = get_stem(stu) + "_results" + (".pkl", ".json")[output_type == "json"]

    if os.path.splitext(stu)[1] == ".ipynb":
        stu = StudentImplementation(stu, output=output)
    else:
        try:
            stu = StudentImplementation.load(stu)
        except:
            raise RuntimeError(f"Could not load the student implementation {stu}")

    res = stu.check(ref)

    if output_type == "pickle":
        if isinstance(res, list):
            with open(dest, "wb+") as f:
                dill.dump(res, f)
        else:
            res.dump(dest)
    elif output_type == "json":
        if isinstance(res, list):
            d = [r.to_dict() for r in res]
        else:
            d = res.to_dict()
        with open(dest, "w+") as f:
            json.dump(d, f, indent=2)
    elif output_type == "report":
        report = generate_report(res)
        click.echo(report)


@click_cli.command()
@click.option("-p", "--parallel", is_flag=True, default=False, 
              help="Execute notebooks in parallel using the multiprocessing library")
@click.option("-d", "--dest", default=None, type=click.Path(), 
              help="Path at which to write the pickled student implementation")
@click.option("--timeout", default=1200, type=click.INT, 
              help="Timeout for notebook execution in seconds")
@click.argument("subm", nargs=-1, type=click.Path(exists=True, dir_okay=False))
def execute(subm, parallel, dest, timeout):
    """
    Execute student submissions to generate memory footprints.

    Executes the student submission(s) SUBM at writes the pickled objects to some output file. If
    DEST is unspecified, this defaults to "./{SUBM.stem}.pkl" (e.g. for SUBM 
    "submissions/subm01.ipynb", this is "./subm01.pkl").
    """
    if len(subm) == 0:
        raise ValueError("You must specify at least one notebook to execute")

    stus = generate_student_impls(subm, parallel=parallel, timeout=timeout)

    if dest is None:
            dest = "./"

    if len(subm) == 1:
        if os.path.isdir(dest):
            stem = get_stem(subm[0])
            output = os.path.join(dest, stem + ".pkl")

        stus[0].dump(output)

    else:
        if not os.path.isdir(dest):
            raise ValueError(f"Destination directory {dest} does not exist or is not a directory")

        for s, stu in zip(subm, stus):
            stem = get_stem(s)
            path = os.path.join(dest, stem + ".pkl")
            stu.dump(path)


def cli(*args, **kwargs):
    """
    Wrapper for the click CLI that sets the prog name.
    """
    prog_name = kwargs.pop("prog_name", "pybryt")
    return click_cli(*args, prog_name=prog_name, **kwargs)
