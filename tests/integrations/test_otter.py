"""Tests for PyBryt's Otter plugin"""

import os
import base64
import shutil
import tempfile
import nbformat
import pathlib
import dill
import pkg_resources
import pytest

from otter.assign.assignment import Assignment
from otter.test_files import GradingResults 
from textwrap import dedent
from unittest import mock

from pybryt import ReferenceImplementation
from pybryt.integrations.otter import OtterPlugin

from ..test_reference import generate_reference_notebook
from ..test_student import generate_student_notebook


def generate_assignment_config(master, result, **kwargs):
    a = Assignment()
    a.master = master
    a.result = result
    a.update(kwargs)
    return a


def test_during_assign():
    nb = generate_reference_notebook()
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as ntf:
        nbformat.write(nb, ntf)
        ntf.seek(0)
        plg = OtterPlugin("", {}, {"references": [ntf.name]})

        rdir = pathlib.Path(tempfile.mkdtemp())
        os.makedirs(rdir / 'autograder')
        os.makedirs(rdir / 'student')

        assignment = generate_assignment_config("", rdir)

        plg.during_assign(assignment)

        ntf_stem = pathlib.Path(ntf.name).stem

        try:
            agref, stref = str((rdir / 'autograder' / ntf_stem).with_suffix(".pkl")), \
                str((rdir / 'student' / ntf_stem).with_suffix(".pkl"))
            # breakpoint()
            assert os.path.isfile(agref)
            assert os.path.isfile(stref)

            # refs = ReferenceImplementation.load(agref)
            with open(agref, "rb") as f:
                refs = dill.load(f)
            assert isinstance(refs, list)
            assert len(refs) == 1
            assert isinstance(refs[0], ReferenceImplementation)

            # refs = ReferenceImplementation.load(stref)
            with open(stref, "rb") as f:
                refs = dill.load(f)
            assert isinstance(refs, list)
            assert len(refs) == 1
            assert isinstance(refs[0], ReferenceImplementation)

        except:
            shutil.rmtree(rdir)
            raise

        else:
            shutil.rmtree(rdir)


def test_during_generate():
    nb = generate_reference_notebook()
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as ntf:
        nbformat.write(nb, ntf)
        ntf.seek(0)

        otter_config = {
            "plugins": [
                {
                    OtterPlugin.IMPORTABLE_NAME: {
                        "references": [ntf.name]
                    }
                }
            ]
        }

        plg = OtterPlugin("", {}, {"references": [ntf.name]})
        plg.during_generate(otter_config, None)

        cfg = otter_config["plugins"][0][OtterPlugin.IMPORTABLE_NAME]
        assert "reference_bytes" in cfg

        refs = dill.loads(base64.b64decode(cfg["reference_bytes"]))
        assert isinstance(refs, list)
        assert len(refs) == 1
        assert isinstance(refs[0], ReferenceImplementation)

    # test after running with otter assign
    plg._cached_refs = refs
    with mock.patch("os.chdir"):
        plg.during_generate(otter_config, generate_assignment_config(pathlib.Path(os.getcwd()), ""))

        cfg = otter_config["plugins"][0][OtterPlugin.IMPORTABLE_NAME]
        assert "reference_bytes" in cfg

        refs = dill.loads(base64.b64decode(cfg["reference_bytes"]))
        assert isinstance(refs, list)
        assert len(refs) == 1
        assert isinstance(refs[0], ReferenceImplementation)


def test_from_notebook(capsys):
    nb = generate_student_notebook()

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as ntf:
        nb.cells.append(nbformat.v4.new_code_cell(dedent(f"""\
            import otter
            grader = otter.Notebook("{ntf.name}")
            grader.run_plugin("pybryt.integrations.otter.OtterPlugin", "ref.sey")
            grader.add_plugin_files("pybryt.integrations.otter.OtterPlugin")
        """)))

        nbformat.write(nb, ntf)
        ntf.seek(0)

        ref_path = str(pathlib.Path(__file__).parent.parent / 'files' / 'expected_ref.pkl')

        plg = OtterPlugin(ntf.name, {}, {})
        with pytest.warns(UserWarning, match="ould not force-save notebook; the results of this "
                                "call will be based on the last saved version of this notebook."):
            plg.from_notebook(ref_path)

        captured = capsys.readouterr()
        expected = dedent("""\
            PyBryt Reference Messages:
            - SUCCESS: Sorted the sample correctly
            - SUCCESS: Computed the size of the sample
            - SUCCESS: computed the correct median

            REFERENCE SATISFIED
        """)
        assert captured.out == expected

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as ntf:
        nbformat.write(nbformat.v4.new_notebook(), ntf)
        ntf.seek(0)

        plg = OtterPlugin(ntf.name, {}, {})

        with pytest.warns(UserWarning, match="ould not force-save notebook; the results of this "
                                "call will be based on the last saved version of this notebook."):
            plg.from_notebook(ref_path)

        captured = capsys.readouterr()
        expected = dedent("""\
            PyBryt Reference Messages:
            - ERROR: The sample was not sorted
            - ERROR: Did not capture the size of the set to determine if it is odd or even
            - ERROR: failed to compute the median

            NO REFERENCE SATISFIED
        """)
        assert captured.out == expected
