# Changelog

All notable changes to this project will be documented in this file, and this project adheres to 
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

* Added time complexity annotations and checking

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
