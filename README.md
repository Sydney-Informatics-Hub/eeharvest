# eeharvest

[![Project generated with
PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)
[![codecov](https://codecov.io/gh/Sydney-Informatics-Hub/eeharvest/branch/main/graph/badge.svg?token=KOEXHJBR2I)](https://codecov.io/gh/Sydney-Informatics-Hub/eeharvest)
[![PyPI-Server](https://img.shields.io/pypi/v/eeharvest.svg)](https://pypi.org/project/eeharvest/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/eeharvest.svg)](https://anaconda.org/conda-forge/eeharvest)
<!-- [![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/eeharvest.svg)](https://anaconda.org/conda-forge/eeharvest) -->

<!-- These are examples of badges you might also want to add to your README. Update the URLs accordingly. -->
<!-- [![Coveralls](https://img.shields.io/coveralls/github/<USER>/eeharvest/main.svg)](https://coveralls.io/r/<USER>/eeharvest) -->
<!-- [![Built Status](https://api.cirrus-ci.com/github/<USER>/eeharvest.svg?branch=main)](https://cirrus-ci.com/github/<USER>/eeharvest) -->
<!-- [![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/eeharvest.svg)](https://anaconda.org/conda-forge/eeharvest) -->
<!-- [![Monthly Downloads](https://pepy.tech/badge/eeharvest/month)](https://pepy.tech/project/eeharvest) -->
<!-- [![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/eeharvest) -->

An [Agricultural Research Federation] (AgReFed) project, the `eeharvest` package
simplifies access to Google Earth Engine and its data catalog with a trio of
convenient methods to collect, process and download data:

- `preprocess()`: server-side processing, cloud and shadow masking, image
  reduction and calculation of spectral indices
- `aggregate()`: **🚧(work-in-progress)🚧** perform additional temporal aggregaton
  on data
- `download()`: download data collection(s) to disk without limits on size or
  number of files

### Why `eeharvest`?

This package is part of the AgReFed [Geodata-Harvester] project which extends
the vision of providing Findable, Accessible, Interoperable and Reusable (FAIR)
agricultural data (and beyond) to Australian researchers and stakeholders. 

The Geodata-Harvester project enables researchers with convenient and reusable
workflows and provides open-source software for automatic data extraction from a
wide range of data sources including spatial-temporal processing. The
`eeharvest` package provides access to data beyond the shores of Australia,
therefore it has been designed to work as a standalone product for anyone to
use.

## Features

- [x] **Download** from any dataset available on the [Google Earth Engine Data Catalog]
- [x] Perform automatic cloud and shadow **masking** (credit: `eemont`)
- [x] **Scale** and **offset** image bands instantly (credit: `eemont`)
- [x] **Spatial** aggregation/reduction (e.g. median)
- [ ] **Temporal** aggregation/reduction (🚧 _in progress_ 🚧)
- [x] Quickly calculate from a vast library of **spectral indices**, e.g. NDVI, BAI (credit: [Awesome Spectral Indices])
- [x] **Preview** assets instantly using interactive **maps**, including calculated spectral
  indices (credit: `geemap`)
- [x] **Downlod** any number of image assets with (almost) no size limits - _please
  be sensible with this feature_ (credit:
  `geedim`)
- [x] **Automate** _all_ of the above with the use of **YAML** config files

[Google Earth Engine Data Catalog]: https://developers.google.com/earth-engine/datasets/catalog
[Awesome Spectral Indices]:
    https://github.com/awesome-spectral-indices/awesome-spectral-indices
[geodata-harvester]: https://github.com/Sydney-Informatics-Hub/geodata-harvester

## Examples

```python
from eeharvest import harvester

harvester.initialise()

# specify collection, coordinates and date range
img = harvester.collect(
        collection="LANDSAT/LC08/C02/T1_L2",
        coords=[149.799, -30.31, 149.80, -30.309],
        date_min="2019-01-01",
        date_max="2019-02-01",
    )

# cloud and shadow masking, spatial aggregation, NDVI calculation
img.preprocess(mask_clouds=True, reduce="median", spectral="NDVI")

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
[rasterio](https://rasterio.readthedocs.io/en/latest/installation.html) website.
For the Google Cloud SDK, follow the instructions on the [gcloud
CLI](https://cloud.google.com/sdk/docs/install) website.

### Conda - *recommended*

```sh
conda install -c conda-forge eeharvest 
```

### Pip

```sh
pip install eeharvest
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
