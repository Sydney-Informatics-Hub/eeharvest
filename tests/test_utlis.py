import ee
import pytest

from eeharvest import utils


def test_suppress_stdout(capsys):
    """Test the suppress_stdout function"""
    with utils.suppress():
        print("This should not be printed")
    captured = capsys.readouterr()
    assert "This should not be printed" not in captured.out


def test_get_indices():
    """
    Test that the get_indices function downloads the list of indices from
    Awesome Spectral Indices and prints them as a dict
    """
    assert type(utils.get_indices()) is dict


def test_imageID_to_tifID(ee_imagecollection):
    """
    Test that the imageID_to_tifID function extracts image IDs from an
    ee.ImageCollection and returns a list of names in .tif format
    """
    assert type(utils.imageID_to_tifID(ee_imagecollection)) is list
