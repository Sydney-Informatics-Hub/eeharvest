"""
    Dummy conftest.py for eeharvest.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""


from pathlib import Path

import ee
import pytest


@pytest.fixture(scope="session", autouse=True)
def data_path():
    """Fixture for the data path"""
    return Path(__file__).parent.joinpath("data")


@pytest.fixture(scope="session", autouse=True)
def coords():
    """Fixture for a set of coordinates"""
    return [149.769345, -30.335861, 149.809173, -30.296271]


@pytest.fixture(scope="session", autouse=True)
def geom_aoi(coords):
    """Fixture coordinates converted to an ee.Geometry object"""
    return ee.Geometry.Rectangle(coords)


@pytest.fixture(scope="session", autouse=True)
def ee_imagecollection(coords):
    """Fixture for an ee.ImageCollection"""
    ee.Initialize()
    img = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
    img = img.filterDate("2019-01-01", "2019-02-01")
    return img.filterBounds(ee.Geometry.Rectangle(coords))


@pytest.fixture(scope="session", autouse=True)
def ee_image(ee_imagecollection):
    """Fixture for an ee.Image"""
    return ee_imagecollection.first()
