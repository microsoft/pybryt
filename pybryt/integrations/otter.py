"""PyBryt plugin for Otter-Grader"""

import os
import dill
import shutil
import base64
import itertools
import warnings
import nbformat

from glob import glob
from otter.assign.assignment import Assignment
from otter.plugins import AbstractOtterPlugin
from otter.test_files import GradingResults
from otter.utils import get_source
from typing import Any, Dict, List, Optional, Union

from .. import ReferenceImplementation, StudentImplementation
from ..execution import NBFORMAT_VERSION
from ..utils import save_notebook


class OtterPlugin(AbstractOtterPlugin):
    """
    Plugin for Otter-Grader.
    """

    IMPORTABLE_NAME = "pybryt.integrations.otter.OtterPlugin"
    _cached_refs = None
    _generate_report = None
    _student_impl = None

    def during_assign(self, assignment: Assignment) -> None:
        """
        This event runs during ``otter assign`` and compiles the list of references indicated in the
        plugin config, placing the pickled reference implementations in the otuput directories. The
        stem of the filename for each reference is kept the same.

        Args:
            assignment (``otter.assign.assignment.Assignment``): the assignment configurations
        """
        self._cached_refs = []
        for fn in self.plugin_config["references"]:
            ref = ReferenceImplementation.compile(fn)
            if not isinstance(ref, list):
                ref = [ref]
            
            self._cached_refs.extend(ref)
            
            ref_fn = os.path.splitext(os.path.split(fn)[1])[0] + ".pkl"
            agp = assignment.result / 'autograder' / ref_fn
            with open(agp, "wb+") as f:
                dill.dump(ref, f)
            
            stp = assignment.result / 'student' / ref_fn
            shutil.copy(str(agp), str(stp))

    def during_generate(self, otter_config: Dict[str, Any], assignment: Assignment) -> None:
        """
        This event runs during ``otter generate`` and, if ``otter assign`` was run, adds the cached
        reference implementations from that run or compiles the indicated references if it was not
        into the ``otter_config`` as a base-64-encoded string.

        Args:
            otter_config (``dict``): the grading configurations
            assignment (``otter.assign.assignment.Assignment``): the assignment configurations; 
                should be set to ``None`` if ``otter assign`` was not run
        """
        if assignment is not None:
            cwd = os.getcwd()
            os.chdir(assignment.master.parent)

        cfg_idx = [self.IMPORTABLE_NAME in c.keys() if isinstance(c, dict) else False for c in otter_config["plugins"]].index(True)
        if self._cached_refs is None:
            refs = []
            for fn in otter_config["plugins"][cfg_idx][self.IMPORTABLE_NAME]["references"]:
                ref = ReferenceImplementation.compile(fn)
                if not isinstance(ref, list):
                    ref = [ref]
                refs.extend(ref)
        else:
            # if during_assign was run, this should be the same
            refs = self._cached_refs
        
        refs = base64.b64encode(dill.dumps(refs)).decode("ascii")
        otter_config["plugins"][cfg_idx][self.IMPORTABLE_NAME]["reference_bytes"] = refs

        if assignment is not None:
            os.chdir(cwd)

    def _generate_impl_report(self, refs: List[ReferenceImplementation], group: Optional[str] = None) -> None:
        """
        Generates and caches a student implementation from the submission path being graded as well
        as a report of what reference(s) were satisfied, if any, and the messages received from 
        those references.

        Args:
            refs (``list[ReferenceImplementation]``): the reference implementations to check against
            group (``str``, optional): a specific question group to run
        """
        nb = nbformat.read(self.submission_path, as_version=NBFORMAT_VERSION)
        self._remove_plugin_calls(nb)

        stu = StudentImplementation(nb)
        results = stu.check(refs, group=group)

        correct = [r.correct for r in results]
        
        report = f"PyBryt Reference Messages:\n"
        
        if any(correct):
            results = [results[correct.index(True)]]
            ending = "\nREFERENCE SATISFIED"

        else:
            ending = "\nNO REFERENCE SATISFIED"

        # TODO: separate mssages for separate references
        for m in itertools.chain(*(r.messages for r in results)):
            report += f"- {m}\n"
        
        report += ending

        self._generated_report = report
        self._student_impl = stu
    
    def _cache_student_impl(self, results: GradingResults, stu: StudentImplementation) -> None:
        """
        Caches the student implementation object as a base-64-encoded string in the grading results
        to be retrieved outside of the grading process.

        Args:
            results (``otter.test_files.GradingResults``): the grading results
            stu (``StudentImplementation``): the student implementation to cache
        """
        encoded_stu = stu.dumps()
        data = results.get_plugin_data(self.IMPORTABLE_NAME, {})
        data["cached_student_impl"] = encoded_stu
        results.set_plugin_data(self.IMPORTABLE_NAME, data)

    @classmethod
    def _remove_plugin_calls(cls, nb: Dict[str, Any]) -> None:
        """
        Removes calls to this Otter plugin from a notebook to ensure that a loop isn't created.
        Modifies the notebook in-place.

        Args:
            nb (``dict``): the notebook to remove calls from
        """
        for cell in nb['cells']:
            source = get_source(cell)
            for i in range(len(source)):
                if f".run_plugin(\"{cls.IMPORTABLE_NAME}\"" in source[i] or \
                        f".add_plugin_files(\"{cls.IMPORTABLE_NAME}\"" in source[i]:
                    source[i] = "# " + source[i]
            cell["source"] = "\n".join(source)

    def from_notebook(self, *ref_paths: str, group: Optional[str] = None) -> None:
        """
        This event runs when ``otter.Notebook.run_plugin`` is called to execute this plugin. It
        attempts to force-save the notebook and then loads the references indicated and generates
        an implementation report by running the references against the student's notebook. Prints
        the generated report to stdout.

        Args:
            *ref_paths (``str``): paths to reference implementation files
            group (``str``, optional): a specific question group to run
        """
        saved = save_notebook(self.submission_path)
        if not saved:
            warnings.warn(
                "Could not force-save notebook; the results of this call will be based on the last "
                "saved version of this notebook."
            )

        refs = []
        for rp in ref_paths:
            with open(rp, "rb") as f:
                ref = dill.load(f)
            # ref = ReferenceImplementation.load(rp)
            if isinstance(ref, ReferenceImplementation):
                refs.append(ref)
            else:
                refs.extend(ref)
        
        self._generate_impl_report(refs, group=group)
        print(self._generated_report)
    
    def notebook_export(self, dest: str = "student.pkl") -> List[str]:
        """
        Dumps the cached student implementation from a called to ``from_notebook`` into a file and
        returns the path to that file for exporting in the zip file.

        Args:
            dest (``str``, optional): the path at which to write the student implementation file
        """
        if self._student_impl is not None:
            self._student_impl.dump(dest)
        else:
            raise RuntimeError("Could not find a cached student implementation to export")
        return [dest]

    def before_execution(self, submission: Dict[str, Any]) -> dict:
        """
        Preprocessor for removing calls to the PyBryt plugin from a notebook before it is executed.

        Args:
            submission (``dict``): the submission notebook
        
        Returns:
            ``dict``: the modified submission notebook
        """
        self._remove_plugin_calls(submission)
        return submission

    def after_grading(self, results: GradingResults) -> None:
        """
        Generates an implementation report and caches the student implementation in the grading 
        results.

        Args:
            results (``otter.test_files.GradingResults``): the grading results
        """
        if self._student_impl is None:
            ref_bytes = base64.b64decode(self.plugin_config["reference_bytes"])
            refs = dill.loads(ref_bytes)
            self._generate_impl_report(refs)
        
        self._cache_student_impl(results, self._student_impl)

    def generate_report(self) -> str:
        """
        Returns the cached report, if present; otherwise, generates the implementation report and
        returns it.

        Returns:
            ``str``: the implementation report
        """
        if self._generated_report is None:
            ref_bytes = base64.b64decode(self.plugin_config["reference_bytes"])
            refs = dill.loads(ref_bytes)
            self._generate_impl_report(refs)
        
        return self._generated_report
    
    @classmethod
    def load_cached_implementations(cls, results: Union[GradingResults, List[GradingResults]]) -> \
            Union[StudentImplementation, List[StudentImplementation]]:
        """
        Loads any student implementations cached in the provided grading results.

        Args:
            results (``otter.test_files.GradingResults`` or ``list[otter.test_files.GradingResults]``):
                one or more grading results
        
        Returns:
            ``Union[StudentImplementation, List[StudentImplementation]]``: a student implementation,
            if a single result was passed, or a list thereof
        """
        if isinstance(results, GradingResults):
            data = results.get_plugin_data(cls.IMPORTABLE_NAME)["cached_student_impl"]
            return StudentImplementation.loads(data)
        elif isinstance(results, list):
            if not all(isinstance(r, GradingResults) for r in results):
                raise TypeError("Object of unexpected type received in results")
            data = [r.get_plugin_data(cls.IMPORTABLE_NAME) for r in results]
            return [StudentImplementation.loads(d["cached_student_impl"]) for d in data]
        else:
            raise TypeError("invalid type for argument 'results'")
