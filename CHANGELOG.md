# Changelog

All notable changes to this project will be documented in this file, and this project adheres to 
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

* Added complexity unions for combining complexity classes per [#155](https://github.com/microsoft/pybryt/issues/155)
* Added a return value annotation per [#144](https://github.com/microsoft/pybryt/issues/144)
* Updated the notebook execution template to use `FrameTracer`

## 0.4.0 - 2022-01-12

* Added the `RequireImport` and `ForbidImport` annotations per [#123](https://github.com/microsoft/pybryt/issues/123)
* Added `TimeComplexityChecker` for analyzing complexity without annotations per [#137](https://github.com/microsoft/pybryt/issues/137)
* Fixed annotation message filtering bug per [#145](https://github.com/microsoft/pybryt/issues/145)
* Added `dataclasses` backport to required modules for Python &lt; 3.7
* Added a `group` argument to the `check` context manager per [#146](https://github.com/microsoft/pybryt/issues/146)
* Moved named annotation filtering into `ReferenceImplementation` constructor per [#147](https://github.com/microsoft/pybryt/issues/147)

## 0.3.1 - 2021-12-01

* Fixed a bug that was causing floats to be added to the memory footprint prematurely per resulting in [#125](https://github.com/microsoft/pybryt/issues/125)
* Refactored internal representation of memory footprints to create abstraction barriers

## 0.3.0 - 2021-11-17

* Fixed bug in `Value`s tracking `set`s of numbers
* Fixed bug in timestamp comparison in `BeforeAnnotation`
* Added `Value.check_against` and `Attribute.check_agains` per [#111](https://github.com/microsoft/pybryt/issues/111)
* Added custom equivalence functions for value annotations per [#113](https://github.com/microsoft/pybryt/issues/113)
* Removed the messages section from reports with no messages
* Added debug mode per [#116](https://github.com/microsoft/pybryt/issues/116)
* Fixed ipykernel v6 issue and unpinned ipykernel per [#114](https://github.com/microsoft/pybryt/issues/114)
* Fixed bug in handling empty student implementations per [#101](https://github.com/microsoft/pybryt/issues/101)

## 0.2.0 - 2021-09-01

* Fixed - 'Empty iterable comparison' per [#109](https://github.com/microsoft/pybryt/pull/109)

## 0.1.9 - 2021-08-13

* Fixed - 'Tolerances for iterables' per [#103](https://github.com/microsoft/pybryt/pull/103)
* Updated - 'Incorrect path on getting started doc' per [#104](https://github.com/microsoft/pybryt/pull/104)
* Fixed 'Invalid usage of NoReturn' per [#105](https://github.com/microsoft/pybryt/pull/105)

## 0.1.8 - 2021-06-29

* Added customizable timeout to notebook execution* Changed the notebook execution template to use `pybryt.tracing_on` and `pybryt.tracing_off`

## 0.1.7 - 2021-06-28

* Fixed `pybryt execute` output per [#94](https://github.com/microsoft/pybryt/issues/94)

## 0.1.6 - 2021-06-23

* Added function call tracking to trace function and student implementations
* Fixed bug for Markdown cells in `pybryt.StudentImplementation.errors`

## 0.1.5 - 2021-06-22

* Added tracking and warnings for errors in student notebook execution
* Added the `matrix_transpose` and `list_permutation` invariants
* Fixed code tracing at top level in the `check` context manager
* Added `pybryt.ReferenceImplementation.get` for looking up annotations by name

## 0.1.4 -  2021-06-16

* Fixed bug in `Value` annotations regarding NaN values

## 0.1.3 - 2021-06-15

* Added the `Collection` annotation

## 0.1.2 - 2021-06-14

* Added the `ForbidType` annotation

## 0.1.1 - 2021-06-14

* Added the context manager `pybryt.no_tracing`
* Added caching to `pybryt.check`
* Added scaffold for custom complexity classes

## 0.1.0 - 2021-05-27

* Added time complexity annotations and checking
* Changed tracing function to only increment step counter when tracing student code
* Added relative tolerance to value annotations
* Fixed bug in intermediate variable preprocessor for newer versions of Python
* Added a context manager for checking code against a reference implementation from the same
  notebook
* Added a CLI for interacting with PyBryt

## 0.0.5 - 2021-05-04

* Changed `pybryt.utils.save_notebook` to use `IPython.display.publish_display_data` instead of 
  `IPython.display.display`
* Added tracing control with `pybryt.tracing_off` and `pybryt.tracing_on`
* Changed `pybryt.utils.save_notebook` to only force-save in the classic Jupyter Notebook interface
* Added a JSON-friendly output for results with `pybryt.ReferenceResult.to_dict`

## 0.0.4 - 2021-03-25

* Added Cython and ipykernel to installation dependencies

## 0.0.3 - 2021-03-24

* Patched bug in `UnassignedVarWrapper` from fix in v0.0.2

## 0.0.2 - 2021-03-23

* Changed timestamp to step counter in execution trace function
* Fixed `UnassignedVarWrapper` so that variables in boolean operations are only evaluated when
  necessary

## 0.0.1 - 2021-03-21

* Initial release
