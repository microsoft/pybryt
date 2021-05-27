""""""

import pytest
import nbformat
import tempfile

from click.testing import CliRunner
from unittest import mock

from pybryt import StudentImplementation
from pybryt.cli import click_cli

from .test_reference import generate_reference_notebook


def test_compile():
    """
    """
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as ntf:
        nb = generate_reference_notebook()
        nbformat.write(nb, ntf)
        ntf.seek(0)

        with mock.patch("pybryt.cli.ReferenceImplementation") as mocked_ref:
            result = runner.invoke(click_cli, ["compile", ntf.name])
            assert result.exit_code == 0
            mocked_ref.compile.assert_called_with(ntf.name, name=None)
            mocked_ref.compile.return_value.dump.assert_called_with(None)

            result = runner.invoke(click_cli, ["compile", ntf.name, "-n", "foo"])
            assert result.exit_code == 0
            mocked_ref.compile.assert_called_with(ntf.name, name="foo")
            mocked_ref.compile.return_value.dump.assert_called_with(None)

            result = runner.invoke(click_cli, ["compile", ntf.name, "-d", "foo.pkl"])
            assert result.exit_code == 0
            mocked_ref.compile.assert_called_with(ntf.name, name=None)
            mocked_ref.compile.return_value.dump.assert_called_with("foo.pkl")


def test_execute():
    """
    """
    runner = CliRunner()
    num_subms = 10
    ntfs = []
    nb = generate_reference_notebook()
    for _ in range(num_subms):
        ntf = tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb")
        nbformat.write(nb, ntf)
        ntf.seek(0)
        ntfs.append(ntf)

    fns = tuple(ntf.name for ntf in ntfs)

    with mock.patch("pybryt.cli.generate_student_impls") as mocked_generate:
        mocked_generate.return_value.__iter__.return_value = (
            iter([mock.create_autospec(StudentImplementation) for _ in range(num_subms)])
        )

        result = runner.invoke(click_cli, ["execute", *fns])
        assert result.exit_code == 0
        mocked_generate.assert_called_with(fns, parallel=False)

        result = runner.invoke(click_cli, ["execute", fns[0]])
        assert result.exit_code == 0
        mocked_generate.assert_called_with((fns[0], ), parallel=False)

        result = runner.invoke(click_cli, ["execute", "-p", *fns])
        assert result.exit_code == 0
        mocked_generate.assert_called_with(fns, parallel=True)

        # check for error on nonexistance output dir
        result = runner.invoke(click_cli, ["execute", *fns, "-o", "/some/fake/path"])
        assert result.exit_code == 1
        assert isinstance(result.exception, ValueError)
        assert result.exception.args[0] == "Output directory /some/fake/path does not exist or is not a directory"

    # check other errors
    result = runner.invoke(click_cli, ["execute"])
    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)
    assert result.exception.args[0] == "You must specify at least one notebook to execute"


def test_cli_func(capsys):
    """
    Checks that the prog name is set correctly.
    """
    from pybryt.__main__ import cli
    try:
        cli(["--help"])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert captured.out.startswith("Usage: pybryt [")
