""""""

import nbformat
import tempfile

from click.testing import CliRunner
from unittest import mock

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
