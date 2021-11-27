""""""

import nbformat
import tempfile

from click.testing import CliRunner
from unittest import mock

from pybryt import StudentImplementation
from pybryt.cli import click_cli
from pybryt.utils import get_stem

from .test_reference import generate_reference_notebook


def test_check():
    """
    """
    runner = CliRunner()
    with mock.patch("pybryt.cli.ReferenceImplementation") as mocked_ref, \
            mock.patch("pybryt.cli.StudentImplementation") as mocked_stu, \
            mock.patch("pybryt.cli.dill") as mocked_dill, \
            mock.patch("pybryt.cli.json") as mocked_json, \
            mock.patch("pybryt.cli.open") as mocked_open:
        mocked_stu.return_value = mock.create_autospec(StudentImplementation)

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as ref_ntf, \
                tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as stu_ntf:
            result = runner.invoke(click_cli, ["check", ref_ntf.name, stu_ntf.name])
            assert result.exit_code == 0
            mocked_ref.compile.assert_called_with(ref_ntf.name)
            mocked_stu.assert_called_with(stu_ntf.name, output=None)
            mocked_stu.return_value.check.return_value.dump.assert_called_with(get_stem(stu_ntf.name) + "_results.pkl")

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".pkl") as ref_ntf, \
                tempfile.NamedTemporaryFile(mode="w+", suffix=".pkl") as stu_ntf:
            result = runner.invoke(click_cli, ["check", ref_ntf.name, stu_ntf.name, "-t", "json"])
            assert result.exit_code == 0
            mocked_ref.load.assert_called_with(ref_ntf.name)
            mocked_stu.load.assert_called_with(stu_ntf.name)
            mocked_stu.load.return_value.check.return_value.to_dict.assert_called_with()
            mocked_json.dump.assert_called()

            with mock.patch("pybryt.cli.generate_report") as mocked_report:
                result = runner.invoke(click_cli, ["check", ref_ntf.name, stu_ntf.name, "-t", "report"])
                assert result.exit_code == 0
                mocked_ref.load.assert_called_with(ref_ntf.name)
                mocked_stu.load.assert_called_with(stu_ntf.name)
                mocked_report.assert_called_with(mocked_stu.load.return_value.check.return_value)

            # check with list of references
            mocked_ref.load.return_value = []
            mocked_stu.load.return_value.check.return_value = []
            
            result = runner.invoke(click_cli, ["check", ref_ntf.name, stu_ntf.name])
            assert result.exit_code == 0
            mocked_ref.load.assert_called_with(ref_ntf.name)
            mocked_stu.load.assert_called_with(stu_ntf.name)
            mocked_dill.dump.assert_called()

            result = runner.invoke(click_cli, ["check", ref_ntf.name, stu_ntf.name, "-t", "json"])
            assert result.exit_code == 0
            mocked_ref.load.assert_called_with(ref_ntf.name)
            mocked_stu.load.assert_called_with(stu_ntf.name)
            mocked_json.dump.assert_called()

            # check errors
            mocked_stu.load.side_effect = Exception()
            result = runner.invoke(click_cli, ["check", ref_ntf.name, stu_ntf.name])
            assert result.exit_code == 1
            assert isinstance(result.exception, RuntimeError)
            assert result.exception.args[0] == f"Could not load the student implementation {stu_ntf.name}"

            mocked_ref.load.side_effect = Exception()
            result = runner.invoke(click_cli, ["check", ref_ntf.name, stu_ntf.name])
            assert result.exit_code == 1
            assert isinstance(result.exception, RuntimeError)
            assert result.exception.args[0] == f"Could not load the reference implementation {ref_ntf.name}"


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
        mocked_generate.assert_called_with(fns, parallel=False, timeout=1200)

        result = runner.invoke(click_cli, ["execute", fns[0]])
        assert result.exit_code == 0
        mocked_generate.assert_called_with((fns[0], ), parallel=False, timeout=1200)

        result = runner.invoke(click_cli, ["execute", "-p", *fns])
        assert result.exit_code == 0
        mocked_generate.assert_called_with(fns, parallel=True, timeout=1200)

        result = runner.invoke(click_cli, ["execute", *fns, "--timeout", "100"])
        assert result.exit_code == 0
        mocked_generate.assert_called_with(fns, parallel=False, timeout=100)

        # check for error on nonexistance output dir
        result = runner.invoke(click_cli, ["execute", *fns, "-d", "/some/fake/path"])
        assert result.exit_code == 1
        assert isinstance(result.exception, ValueError)
        assert result.exception.args[0] == "Destination directory /some/fake/path does not exist or is not a directory"

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
