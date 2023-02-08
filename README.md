# eeharvest

<p align="center">
  <a href="https://github.com/Sydney-Informatics-Hub/eeharvest"><img src="https://github.com/Sydney-Informatics-Hub/eeharvest/blob/main/docs/_static/eeharvest.png" alt="header" width="200"></a>
</p>

[![Project generated with
PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)
[![codecov](https://codecov.io/github/Sydney-Informatics-Hub/eeharvest/branch/main/graph/badge.svg?token=KOEXHJBR2I)](https://codecov.io/github/Sydney-Informatics-Hub/eeharvest)
[![PyPI-Server](https://img.shields.io/pypi/v/eeharvest.svg)](https://pypi.org/project/eeharvest/)
[![Conda
Version](https://img.shields.io/conda/vn/conda-forge/eeharvest.svg)](https://anaconda.org/conda-forge/eeharvest)
[![Monthly Downloads](https://pepy.tech/badge/eeharvest/month)](https://pepy.tech/project/eeharvest)
![GitHub last
commit](https://img.shields.io/github/last-commit/Sydney-Informatics-Hub/eeharvest)

An [Agricultural Research Federation] (AgReFed) project, the `eeharvest` package
simplifies access to Google Earth Engine and its data catalog with a quartet of
convenient methods to collect, process and download data:

- `preprocess()`: server-side processing, cloud and shadow masking, image
  reduction and calculation of spectral indices
- `aggregate()`: **🚧(work-in-progress)🚧** perform additional temporal aggregaton
  on data
- `download()`: download data collection(s) to disk without limits on size or
  number of files
- `map()`: preview assets automatically in an interactive map

**⚠ WARNING:** `eeharvest` does only a few things, but it does them well. The
main objective is to provide a simple, *intuitive* interface to Google Earth
Engine that is easy to use and understand for researchers who may *not* have a
lot of experience with Python or Google Earth Engine, but they "just want to
download some maps".  **Most importantly, `eeharvest` is designed to be used with
`geodata-harvester` for fully automated and reproducible data extraction and
processing**, but we understand the benefits of using it as a standalone package.

If you are an advanced user, we recommend that you use the
Earth Engine API directly (but see useful add-on packages such as `eemont` and
`geemap` in our acknowledgements below).

## Why `eeharvest`?

This package is part of the AgReFed [Geodata-Harvester] project which extends
the vision of providing Findable, Accessible, Interoperable and Reusable (FAIR)
agricultural data (and beyond) to Australian researchers and stakeholders.

There are currently three packages that have been produced under AgReFed:

- 🐍 `geodata-harvester` ([link]()): a Python package for data extraction and processing from a
  wide range of data sources in Australia, with support for Google Earth Engine
  via a dependency on `eeharvest` (see below)
- 🐍 `eeharvest`: **this package**, which provides access to Google Earth Engine
  and is designed to work as a standalone package
- **R** `dataharvester` ([link]()): an R package that replicates the functionality of
  `geodata-harvester`, but with additional support for functional R programming
  and the tidyverse

## Features

- ✅ **Download** from any dataset available on the [Google Earth Engine Data Catalog]
- ✅ Perform automatic cloud and shadow **masking** (credit: `eemont`)
- ✅ **Scale** and **offset** image bands instantly (credit: `eemont`)
- ✅ **Spatial** aggregation/reduction (e.g. median)
- ❌ **Temporal** aggregation/reduction (🚧 _work-in-progress_ 🚧)
- ✅ Quickly calculate from a vast library of **spectral indices**, e.g. NDVI, BAI (credit: [Awesome Spectral Indices])
- ✅ **Preview** assets instantly using interactive **maps**, including calculated spectral
  indices (credit: `geemap`)
- ✅ **Downlod** any number of image assets with (almost) no size limits - _please
  be sensible with this feature_ (credit:
  `geedim`)
- ✅ **Automate** _all_ of the above with the use of **YAML** config files

[Google Earth Engine Data Catalog]: https://developers.google.com/earth-engine/datasets/catalog
[Awesome Spectral Indices]: https://github.com/awesome-spectral-indices/awesome-spectral-indices
[geodata-harvester]: https://github.com/Sydney-Informatics-Hub/geodata-harvester

## Examples

```python
import eeharvest

eeharvest.initialise()

# specify collection, coordinates and date range
img = eeharvest.collect(
        collection="LANDSAT/LC08/C02/T1_L2",
        coords=[149.799, -30.31, 149.80, -30.309],
        date_min="2019-01-01",
        date_max="2019-02-01",
    )

# cloud and shadow masking, spatial aggregation, NDVI calculation
img.preprocess(mask_clouds=True, reduce="median", spectral="NDVI")

# visualise (optional, but fun)
img.map(bands="NDVI")

# download to disk (defaults to a "downloads" folder in working directory)
img.download(bands="NDVI")
```

## Installation

### Installing dependencies from conda

Before installing the package you may need to install the following packages
manually:

- [GDAL](https://gdal.org/download.html): to manipulate raster and vector
  geospatial data
- [gcloud
  CLI](https://cloud.google.com/sdk/docs/install): needed to authenticate
  to Google servers

In most cases, these can be installed through conda-forge (but see alternatives
below if not):

```sh
conda install -c conda-forge gdal google-cloud-sdk
```

### Installing dependencies from binaries

If conda is somehow not an option, you can install the two dependencies from
binaries. For GDAL, use `apt-get` or `brew` (macOS). Clear instructions have
been written on the
[rasterio](https://rasterio.readthedocs.io/en/latest/installation.html) and [PyPi
GDAL](https://pypi.org/project/GDAL/) websites.
For the Google Cloud SDK, follow the instructions on the [gcloud
CLI](https://cloud.google.com/sdk/docs/install) website.

### Conda - _recommended_

```sh
conda install -c conda-forge eeharvest
```

### Pip

```sh
pip install -U eeharvest
```

<!-- pyscaffold-notes -->

## Attribution and Acknowledgments

This software was developed by the **[Sydney Informatics Hub]**, a core research
facility of the University of Sydney, as part of the Data Harvesting project for
the **[Agricultural Research Federation] (AgReFed)**. AgReFed is supported by the
Australian Research Data Commons (ARDC) and the Australian Government through
the National Collaborative Research Infrastructure Strategy (NCRIS).

Acknowledgments are an important way for us to demonstrate the value we bring to
your research. Your research outcomes are vital for ongoing funding of the
Sydney Informatics Hub. If you make use of this software for your research
project, please include the following acknowledgment:

> This research was supported by the Sydney Informatics Hub, a Core Research
> Facility of the University of Sydney, and the Agricultural Research Federation
> (AgReFed).

## Credits

- [Google Earth Engine API](https://github.com/google/earthengine-api) - Apache License 2.0
- `eemont` [package](https://github.com/davemlz/eemont) - MIT license
- `geedim` [package](https://github.com/dugalh/geedim) - Apache License 2.0
- `geemap` [package](https://github.com/giswqs/geemap) - MIT License
- [Awesome Spectral
  Incices](https://github.com/awesome-spectral-indices/awesome-spectral-indices)
  \- MIT License

## Note

This project has been set up using [PyScaffold] 4.3.1 and the [dsproject
extension] 0.7.2. For more information see [CONTRIBUTING.md](CONTRIBUTING.md) in this repository.

[pyscaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject
[Agricultural Research Federation]: https://www.agrefed.org.au
[Sydney Informatics Hub]: https://www.sydney.edu.au/research/facilities/sydney-informatics-hub.html
