[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

<!-- These are examples of badges you might also want to add to your README. Update the URLs accordingly.
[![Built Status](https://api.cirrus-ci.com/github/<USER>/eeharvest.svg?branch=main)](https://cirrus-ci.com/github/<USER>/eeharvest)
[![ReadTheDocs](https://readthedocs.org/projects/eeharvest/badge/?version=latest)](https://eeharvest.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/eeharvest/main.svg)](https://coveralls.io/r/<USER>/eeharvest)
[![PyPI-Server](https://img.shields.io/pypi/v/eeharvest.svg)](https://pypi.org/project/eeharvest/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/eeharvest.svg)](https://anaconda.org/conda-forge/eeharvest)
[![Monthly Downloads](https://pepy.tech/badge/eeharvest/month)](https://pepy.tech/project/eeharvest)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/eeharvest)
-->

# eeharvest

Part of the AgReFed Data-Harvester project, `eeharvest` aims to simplify
the processing of Google Earth Engine data by leveraging on
already-available python packages: `ee`, `eemont`, `geemap` and `wxee`.

Note: this package does not intend to replace any of the packages above. Rather,
it selects useful functionality which are consolidated into broad methods:

- `preprocess()`: server-side processing, cloud and shadow masking, image
  reduction and calculation of spectral indices
- `aggregate()`: perform additional temporal and/or spatial aggregaton on data
- `map()`: preview data rasters on an interactive map before downloading
- `download()`: download data collection, ready for client-side processing

Read the online documentation for more information.

## Installation

## Project Organization

```
├── AUTHORS.md              <- List of developers and maintainers.
├── CHANGELOG.md            <- Changelog to keep track of new features and fixes.
├── CONTRIBUTING.md         <- Guidelines for contributing to this project.
├── Dockerfile              <- Build a docker container with `docker build .`.
├── LICENSE.txt             <- License as chosen on the command-line.
├── README.md               <- The top-level README for developers.
├── configs                 <- Directory for configurations of model & application.
├── data
│   ├── external            <- Data from third party sources.
│   ├── interim             <- Intermediate data that has been transformed.
│   ├── processed           <- The final, canonical data sets for modeling.
│   └── raw                 <- The original, immutable data dump.
├── docs                    <- Directory for Sphinx documentation in rst or md.
├── environment.yml         <- The conda environment file for reproducibility.
├── models                  <- Trained and serialized models, model predictions,
│                              or model summaries.
├── notebooks               <- Jupyter notebooks. Naming convention is a number (for
│                              ordering), the creator's initials and a description,
│                              e.g. `1.0-fw-initial-data-exploration`.
├── pyproject.toml          <- Build configuration. Don't change! Use `pip install -e .`
│                              to install for development or to build `tox -e build`.
├── references              <- Data dictionaries, manuals, and all other materials.
├── reports                 <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures             <- Generated plots and figures for reports.
├── scripts                 <- Analysis and production scripts which import the
│                              actual PYTHON_PKG, e.g. train_model.
├── setup.cfg               <- Declarative configuration of your project.
├── setup.py                <- [DEPRECATED] Use `python setup.py develop` to install for
│                              development or `python setup.py bdist_wheel` to build.
├── src
│   └── eeharvest           <- Actual Python package where the main functionality goes.
├── tests                   <- Unit tests which can be run with `pytest`.
├── .coveragerc             <- Configuration for coverage reports of unit tests.
├── .isort.cfg              <- Configuration for git hook that sorts imports.
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks.
```

<!-- pyscaffold-notes -->

## Note

This project has been set up using [PyScaffold] 4.3.1 and the [dsproject extension] 0.7.2.

[conda]: https://docs.conda.io/
[pre-commit]: https://pre-commit.com/
[jupyter]: https://jupyter.org/
[nbstripout]: https://github.com/kynan/nbstripout
[google style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[pyscaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject
