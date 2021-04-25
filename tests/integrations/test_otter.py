"""Tests for PyBryt's Otter plugin"""

import os
import base64
import shutil
import tempfile
import nbformat
import pathlib
import dill

from otter.assign.assignment import Assignment
from otter.test_files import GradingResults 
from unittest import mock

from pybryt import ReferenceImplementation
from pybryt.integrations.otter import OtterPlugin

from ..test_reference import generate_reference_notebook


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

            refs = ReferenceImplementation.load(agref)
            assert isinstance(refs, list)
            assert len(refs) == 1
            assert isinstance(refs[0], ReferenceImplementation)

            refs = ReferenceImplementation.load(stref)
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
