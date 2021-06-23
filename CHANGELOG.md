# Changelog

All notable changes to this project will be documented in this file, and this project adheres to 
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
