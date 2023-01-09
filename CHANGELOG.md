# Changelog

🚢: release |
🚨: breaking |
✨: new |
🔒: security |
🛠: improvement
⚡️: performance |
🐞: bugfix |
📖: docs |
⚙️: chore |
♻️: refactor |
🚦: tests |
🎨: style |
📦: build |
🚧: work in progress

## 🚢 Version 1.0.0

🎉🎉🎉 This is it! 🎉🎉🎉

### Changed

- 📖: Update CONTRIBUTING.md, requirements.txt and setup.cfg
- 🐞: Fixed gdal-config error that appeared because gdal dependencies were not
  available in pip but can be configured automatically in conda
- 📦: Improve dependency management and conda settings in tox.ini

## 🚢 Version 0.3.1

### Changed

- 📦: Update dependency lists in tox.ini and environment.yml
- 📖: Update README to better describe package functionality

## 🚢 Version 0.3

### Added

- 🚦: Pytest integration. Tests now cover > 90% of the code

### Changed

- 🐞: Minimum Python version set to 3.9 and above, was 3.11 before
- 📦: Update tox.ini to publish package on [TestPyPi](https://test.pypi.org/) -
  tested and working
- 📖: Update documentation throughout (modules, readme, examples, etc) to prepare
  for eventual publication to PyPi and conda-forge

## 🚢 Version 0.2

### Added

- 📦: Integration with trunk.io, PyScaffold and tox for automated build and
  testing

### Changed

- 🛠: Made some utility functions private so that users won't become confused
  using them
- 🐞: Fix multiple issues due to migration, including module referencing,
  documentation and example code
- 🐞: Fix how paths to config files are obtained by using the `importlib_resources`
  package, which is compatible to Python versions <3.9

## 🚢 Version 0.1

### Added

- 📦: Migration of Google Earth Engine code from the AgReFed Data Harvester
  notebook. Hello `eeharvest`!
