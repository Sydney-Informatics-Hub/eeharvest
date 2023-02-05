## Unreleased (2023-02-03)

### New feature:

- better `auto()` function that can process multiple collections([`ad2854b`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/ad2854b37f5a38ec80ab7f26f2a20803279663cd)) (by Januar Harianto)
- default band list are recognised, even when appended by `reduce`([`6686f59`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/6686f597538370df9661f1bdd9e248c70575d222)) (by Januar Harianto)
- new internal function to insert key value pairs into a nested dict([`2c4fbaa`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/2c4fbaab1e0ef540f8806e84d8d8b186e1f52d48)) (by Januar Harianto)
- internal function to improve image reduction methods([`61bc815`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/61bc8158d14940f7daeff30786274ddeb83ffc28)) (by Januar Harianto)
- internal function that checks config for >1 image collections([`8a8bcde`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/8a8bcde00bdbc361bdfd58880b246638abf3702f)) (by Januar Harianto)
- use either `initialise()` or `initialize()` to authenticate to GEE([`d256b1d`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/d256b1dd06546b05862a1c2d21bf050593e44200)) (by Januar Harianto)

### Bugs fixed:

- raise error when config file/object is not suitable([`30985a7`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/30985a72c3d1206be963c860803e48d082a6761f)) (by Januar Harianto)
- download folder is blank (`NoneType`) due to faulty conditionals([`d524c63`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/d524c633a077a44d0447355a0eaa11a3cab41d6a)) (by Januar Harianto)
- better feedback when initialisation step is complete([`ec0b138`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/ec0b13847a57f1ce1971bd9dc6fd10f54c33a118)) (by Januar Harianto)
- recognise image collection string even if it is a list item([`49e887c`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/49e887ca6b6ea9ebe3f1014a4ee2e0d8ad4131fa)) (by Januar Harianto)
- :bug: `collect()` now works with configs that are already imported as `dict` object([`e85e4bd`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/e85e4bd9cef195ecdfaf7ceefca380358912351b)) (by Januar Harianto)

### Performance improves:

- use any method in GEE's`ee.Reducer` module in `reduce`([`6abc8a0`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/6abc8a00a5d5f0d990c4bba0011df5a7f7e634d4)) (by Januar Harianto)
- `mask_probability` defaults to `None`, which triggers val of 60([`490b0ba`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/490b0baa15a82146b44b5adfd4bc3c34d4687887)) (by Januar Harianto)
- improve image count conditional to capture values less than 1([`7a71aa2`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/7a71aa2c72f1fc45f4720b2d935f5867f064b318)) (by Januar Harianto)

## v1.4.0 (2023-01-24)

### New feature:

- `eeharvest` is now usable in Python 3.8 and above([`d6eb568`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/d6eb56805987758f689fd69b55baeda9497a9536)) (by Januar Harianto)
- enable optional, direct method calls in `eeharvest`([`9f8f6cd`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/9f8f6cd122facc2650eec75755307c2600330623)) (by Januar Harianto)

### Bugs fixed:

- Error validating config file against schema file #5([`186be69`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/186be694de984e7b2707370fa0b6656258c4d476)) (by Januar Harianto), Closes: #5

## v1.3.0 (2023-01-22)

### New feature:

- package is now published on conda-forge - documentation updated([`05e022c`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/05e022c20b45eecdbc22131c7723f623bac5c969)) (by Januar Harianto)

### Bugs fixed:

- ValueError when scale is not set in `download()` function([`96fc23d`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/96fc23ddb6d15edd77ea4e662d360045218b8110)) (by Januar Harianto), Closes: #4
- no directory is created when `outpath` is `None` in `download()`([`3a7aaef`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/3a7aaef2e276327de4eb323d3394943c14f8767f)) (by Januar Harianto)
- better validation of `target_bbox` and/or `infile` keys([`da0a894`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/da0a89446c84a078cd020072f464c4a69533b9c8)) (by Januar Harianto)

## v1.2.0 (2023-01-20)

### New feature:

- `convert_size()` to calculate file sizes before download([`e5aa484`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/e5aa4847e552b3902bbd8e6e710b44dd1deac3b8)) (by Januar Harianto)

## v1.1.0 (2023-01-19)

### New feature:

- add `_validate_bbox()` to validate bounding box value(s)([`7134956`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/71349565d33fd16c54d5d1476beccf5b5ae536e6)) (by Januar Harianto)

### Bugs fixed:

- harvest() validation errors (see notes)([`c94dab2`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/c94dab2d128ac4055e923465f12d9ccaf88ceb38)) (by Januar Harianto)
- error when validating a config file containing non-GEE keys([`2f21247`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/2f2124752144456dc014fa746e62a2070ffc25ef)) (by Januar Harianto)

## v1.0.4 (2023-01-18)

### Bugs fixed:

- `YamaleErrorError` validating a YAML file([`09ca03d`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/09ca03d557ead834aafd2ef163addf336d7510e5)) (by Januar Harianto)

## v1.0.3 (2023-01-18)

### Bugs fixed:

- remove unused imports([`484a10e`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/484a10e771c7118c4eb17e0b6d5e569624a18c42)) (by Januar Harianto)

## v1.0.2 (2023-01-18)

### Bugs fixed:

- disable codecov upload([`deeb811`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/deeb811156c11fa9f2d72b2981a45c3e939f272c)) (by Januar Harianto)
- add missing code in README to initialise to GEE([`7c63659`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/7c636591d0ffb7813ba434c02cb5b3dbfe0aa332)) (by Januar Harianto), Closes: #3

## v1.0.0 (2023-01-18)

### Bugs fixed:

- `download()` can fail due to incorrect object assignment([`f7c5a5c`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/f7c5a5cbb6293f142c7ef6bd04c202f19a7e812d)) (by Januar Harianto), Closes: #2
- same dependency error as before (`importlib_resources`)([`cef4dc2`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/cef4dc2b99bf93922406781c7f20987bf88b7de3)) (by Januar Harianto)
- missing dependency([`d79c528`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/d79c5288e18f7074b4d7829157ec8434784c1bc0)) (by Januar Harianto), Closes: #1

### Performance improves:

- improve prompt to download gcloud cli if needed([`421b411`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/421b411b18cae2f56992e1e73475ed4e597bf0c0)) (by Januar Harianto)

### BREAKING CHANGES:

- the followimg methods now belong to  the harvester module: initialise, get)indices, ee_stac, download_tif,  validate_collections, supported_collections, get_bandinfo

## v0.3.1 (2022-11-29)

## v0.3.0 (2022-11-29)

### New feature:

- add ability to overwrite outpath value in config through function([`8e114e8`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/8e114e83c5434728b1ebfada00a3e8da9f1f8f3b)) (by Januar Harianto)
- new messaging style for titles([`dc8c0ee`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/dc8c0ee8a2d069394787f38a49d2fc99401729cf)) (by Januar Harianto)
- new function to generate unique hash for downloads([`95bf6a3`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/95bf6a3ba9b6a02edeca17c0f1166989b8ec8e9d)) (by Januar Harianto)
- add_missing_keys to always fill in defaults to config file([`33674fd`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/33674fdf3950caf6cf50d79522b2a17a711b8f54)) (by Januar Harianto)
- add schema and config yaml files to src([`f34a9c1`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/f34a9c15268783a0491006dd21f9ea98b878454e)) (by Januar Harianto)
- new settings module to handle config-related functions([`b87e98a`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/b87e98a1d2d35d06e94abfa58900bc9b68dab2cf)) (by Januar Harianto)
- new schema template to validate yaml using yamale([`d3f4273`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/d3f4273bb840851411c8bd4197e077c25b124d44)) (by Januar Harianto)

### Bugs fixed:

- raise exception instead of message to stop run appropriately([`bd108d1`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/bd108d1e88a46586fb5db638e354c6bc4f27791b)) (by Januar Harianto)
- convert paths to string and clarify exception handling([`54b8968`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/54b896801c4810fd14353240207d35ae13daca00)) (by Januar Harianto)
- forgot to update schema.yaml in src([`a590ef9`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/a590ef93f40bb41f704a5854bc3b971c018d2962)) (by Januar Harianto)
- update schema.yaml to accept null value in the reduce key([`bd75e8f`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/bd75e8f54394b9475ede7a2282427013067dff5e)) (by Januar Harianto)
- missing pathlib import([`f322f35`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/f322f35ed8b0e8db8bd44151246fe31e786374e8)) (by Januar Harianto)
- incorrect path to file causing FileNotFound error([`2ccf8bc`](https://github.com/Sydney-Informatics-Hub/eeharvest/commit/2ccf8bc8cb74f69672503f44d694e84ed0516ad8)) (by Januar Harianto)