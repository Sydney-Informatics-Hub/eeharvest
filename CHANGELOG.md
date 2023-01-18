## v1.0.4 (2023-01-18)

### Fix

- `YamaleErrorError` validating a YAML file

## v1.0.3 (2023-01-18)

### Fix

- remove unused imports

## v1.0.2 (2023-01-18)

### Fix

- disable codecov upload

## v1.0.1 (2023-01-18)

### Fix

- add missing code in README to initialise to GEE

## v1.0.0 (2023-01-18)

### BREAKING CHANGE

- the followimg methods now belong to  the harvester module: initialise, get)indices, ee_stac, download_tif,  validate_collections, supported_collections, get_bandinfo

### Fix

- `download()` can fail due to incorrect object assignment
- same dependency error as before (`importlib_resources`)
- missing dependency

### Refactor

- consolidate methods into harvester module

### Perf

- improve prompt to download gcloud cli if needed

## v0.3.1 (2022-11-29)

## v0.3.0 (2022-11-29)

### Feat

- add ability to overwrite outpath value in config through function
- new messaging style for titles
- new function to generate unique hash for downloads
- add_missing_keys to always fill in defaults to config file
- add schema and config yaml files to src
- new settings module to handle config-related functions
- new schema template to validate yaml using yamale

### Fix

- raise exception instead of message to stop run appropriately
- convert paths to string and clarify exception handling
- forgot to update schema.yaml in src
- update schema.yaml to accept null value in the reduce key
- missing pathlib import
- incorrect path to file causing FileNotFound error

### Refactor

- changed some names
