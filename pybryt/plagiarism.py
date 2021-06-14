"""Plagiarism checking for PyBryt"""

import random
import numpy as np

from typing import List, Union

from .annotations import Value
from .reference import ReferenceImplementation, ReferenceResult


def create_references(student_impls: List["StudentImplementation"], frac=0.25, seed=None, 
        filter_none=True, **kwargs) -> List[ReferenceImplementation]:
    """
    """
    if seed is not None:
        random.seed(seed)

    values = [[t[0] for t in stu.values if t[0] is not None] for stu in student_impls]

    k = int(min([len(v) for v in values]) * frac)
    
    refs = []
    for stu, vals in zip(student_impls, values):
        ref_values = random.sample(vals, k)
        refs.append(ReferenceImplementation([Value(v) for v in ref_values]))

    return refs


def get_impl_results(ref_impl: ReferenceImplementation, student_impls: List["StudentImplementation"], 
        arr=True, **kwargs) -> Union[List[ReferenceResult], np.ndarray]:
    """
    Returns matrix where rows are student impls and cols represent whether each value was satisfied
    by the student impl
    """
    # results = []
    # for ref in ref_impls:
    #     ref_results = []
    #     for stu in student_impls:
    #         ref_results.append(stu.check(ref))
    #     results.append(ref_results)

    results = []
    for stu in student_impls:
        results.append(stu.check(ref_impl))
    
    if arr:
        return np.array([r.to_array() for r in results])
    else:
        return results


def compare_implementations(student_impls: List["StudentImplementation"], **kwargs) -> \
        List[Union[List[ReferenceResult], np.ndarray]]:
    """
    """
    refs = create_references(student_impls, **kwargs)
    results = []
    for ref in refs:
        results.append(get_impl_results(ref, student_impls, **kwargs))
    return results


from .student import StudentImplementation
