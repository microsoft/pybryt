"""PyBryt plugin for Otter-Grader"""

import os
import dill
import shutil
import base64
import pathlib
import itertools
import warnings
import nbformat

from glob import glob
from otter.plugins import AbstractOtterPlugin
from otter.test_files import GradingResults
from otter.utils import get_source
from typing import List, NoReturn, Union

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

    def during_assign(self, assignment):
        self._cached_refs = []
        for fn in self.plugin_config["references"]:
            ref = ReferenceImplementation.compile(fn)
            if not isinstance(ref, list):
                ref = [ref]
            
            self._cached_refs.extend(ref)
            
            agp = assignment.result / 'autograder' / (pathlib.Path(fn).stem + ".pkl")
            with open(agp, "wb+") as f:
                dill.dump(ref, f)
            
            stp = assignment.result / 'student' / (pathlib.Path(fn).stem + ".pkl")
            shutil.copy(str(agp), str(stp))

    def during_generate(self, otter_config, assignment):
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

    def _generate_impl_report(self, refs, group=None):
        nb = nbformat.read(self.submission_path, as_version=NBFORMAT_VERSION)
        self._remove_plugin_calls(nb)

        stu = StudentImplementation(nb)
        # # if self.plugin_config.get("student_cache_dir") is not None:
        #     fn = os.path.splitext(os.path.basename(self.submission_path))[0] + ".pkl"
        #     fp = self._cache_student_impl(stu, fn)
        #     cache = f"Student implementation cached at: {fp}\n"
        # else:
        #     cache = ""
        
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
    
    def _cache_student_impl(self, results: GradingResults, stu: StudentImplementation) -> NoReturn:
        # path = self.plugin_config.get("student_cache_dir")
        # if path is None or not os.path.isabs(path):
        #     raise ValueError(f"Invalid student implementation cache directory: {path}")
        # elif not os.path.isdir(path):
        #     raise ValueError(f"Student implementation cache directory does not exist or is a file: {path}")
        # fn = filename
        # fp = os.path.join(path, fn)
        # i = 1
        # while os.path.exists(fp):
        #     stem, ext = os.path.splitext(filename)
        #     fn = stem + f"-{i}" + ext
        #     fp = os.path.join(path, fn)
        #     i += 1
        
        # stu.dump(dest=fp)
        encoded_stu = stu.dumps()
        data = results.get_plugin_data(self.IMPORTABLE_NAME, {})
        data["cached_student_impl"] = encoded_stu
        results.set_plugin_data(self.IMPORTABLE_NAME, data)

    @classmethod
    def _remove_plugin_calls(cls, nb):
        """
        """
        for cell in nb['cells']:
            source = get_source(cell)
            for i in range(len(source)):
                if f".run_plugin(\"{cls.IMPORTABLE_NAME}\"" in source[i] or f".add_plugin_files(\"{cls.IMPORTABLE_NAME}\"" in source[i]:
                    source[i] = "# " + source[i]
            cell["source"] = "\n".join(source)

    def from_notebook(self, *ref_paths, group=None):
        saved = save_notebook(self.submission_path)
        if not saved:
            warnings.warn(
                "Could not force-save notebook; the results of this call will be based on the last "
                "saved version of this notebook."
            )

        refs = []
        for rp in ref_paths:
            ref = ReferenceImplementation.load(rp)
            if isinstance(ref, ReferenceImplementation):
                refs.append(ref)
            else:
                refs.extend(ref)
        
        self._generate_impl_report(refs, group=group)
        print(self._generated_report)
    
    def notebook_export(self, dest="student.pkl"):
        """
        """
        if self._student_impl is not None:
            self._student_impl.dump(dest)
        else:
            raise RuntimeError("Could not find a cached student implementation to export")
        return [dest]

    def before_execution(self, submission):
        self._remove_plugin_calls(submission)
        return submission

    def after_grading(self, results):
        if self._student_impl is None:
            ref_bytes = base64.b64decode(self.plugin_config["reference_bytes"])
            refs = dill.loads(ref_bytes)
            self._generate_impl_report(refs)
        
        self._cache_student_impl(results, self._student_impl)

    def generate_report(self):
        if self._generated_report is None:
            ref_bytes = base64.b64decode(self.plugin_config["reference_bytes"])
            refs = dill.loads(ref_bytes)
            self._generate_impl_report(refs)
        
        return self._generated_report
    
    @classmethod
    def load_cached_implementations(cls, results: Union[GradingResults, List[GradingResults]]) -> \
            Union[StudentImplementation, List[StudentImplementation]]:
        """
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
