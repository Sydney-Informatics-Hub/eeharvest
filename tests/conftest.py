import os
from distutils import dir_util
from pathlib import Path

import ee
import pytest

from eeharvest import harvester


@pytest.fixture(scope="session", autouse=True)
def data_path():
    """Fixture for the data path"""
    return Path(__file__).parent.joinpath("data")


@pytest.fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir


@pytest.fixture(scope="session", autouse=True)
def coords():
    """Fixture for a set of coordinates"""
    return [149.799, -30.31, 149.80, -30.309]


@pytest.fixture(scope="session", autouse=True)
def geom_aoi(coords):
    """Fixture coordinates converted to an ee.Geometry object"""
    harvester.initialise()
    return ee.Geometry.Rectangle(coords)


@pytest.fixture(scope="session", autouse=True)
def ee_imagecollection(coords):
    """Fixture for an ee.ImageCollection"""
    harvester.initialise()
    img = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
    img = img.filterDate("2019-01-01", "2019-02-01")
    return img.filterBounds(ee.Geometry.Rectangle(coords))


@pytest.fixture(scope="session", autouse=True)
def ee_image(ee_imagecollection):
    """Fixture for an ee.Image"""
    harvester.initialise()
    return ee_imagecollection.first()


@pytest.fixture(scope="session", autouse=True)
def to_harvest():
    """Fixture for a collect object"""
    harvester.initialise()
    img = harvester.collect(
        collection="LANDSAT/LC08/C02/T1_L2",
        coords=[149.799, -30.31, 149.80, -30.309],
        date_min="2019-01-01",
        date_max="2019-02-01",
    )
    return img
