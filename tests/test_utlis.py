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


def test_validate_collection():
    """
    Test that the validate_collection function returns True if the collection
    is valid and False if it is not
    """
    assert utils.validate_collection("LANDSAT/LC08/C02/T1_L2") is True
    assert utils.validate_collection("MODIS/006/MCD43A4") is True
    assert utils.validate_collection("NOT/A/COLLECTION") is False


def test_get_bandinfo(ee_image):
    """
    Test that the get_bandinfo function returns a list of band names when run
    on an ee.ImageCollection or ee.Image object
    """
    bands = utils.get_bandinfo(ee_image)
    assert type(bands) is list


def test_stretch_minmax_accepts_3_bands(ee_image, geom_aoi):
    """
    stretch_minmax: function returns a list of length 2 when three bands are
    provided, and that it accepts the 'by' argument
    """
    assert (
        len(
            utils.stretch_minmax(
                ee_image=ee_image,
                region=geom_aoi,
                bands=["SR_B1", "SR_B2", "SR_B3"],
                by="percentile",
            )
        )
        == 2
    )
    assert (
        len(
            utils.stretch_minmax(
                ee_image=ee_image,
                region=geom_aoi,
                bands=["SR_B1", "SR_B2", "SR_B3"],
                by="sd",
            )
        )
        == 2
    )


def test_stretch_minmax_accepts_one_band(ee_image, geom_aoi):
    """
    stretch_minmax: function returns a list of length 2 when one band
    is provided
    """
    assert len(utils.stretch_minmax(ee_image, geom_aoi, ["SR_B1"], scale=100)) == 2
    assert len(utils.stretch_minmax(ee_image, geom_aoi, ["SR_B1"], "sd")) == 2


def test_stretch_minmax_produces_exception_if_not_1_or_3_bands_provided(
    ee_image, geom_aoi
):
    """
    stretch_minmax: function raises an exception if not 1 or 3 bands are
    provided
    """
    # Raise error if two bands are provided
    with pytest.raises(IndexError) as excinfo:
        utils.stretch_minmax(ee_image, geom_aoi, ["SR_B1", "SR_B2"])
    assert "list index out of range" in str(excinfo.value)


def test_stretch_minmax_accepts_None_for_bands_argument(ee_image, geom_aoi):
    """
    :stretch_minmax: function accepts False for the bands argument
    """
    # No bands provided i.e. bands=False
    assert len(utils.stretch_minmax(ee_image, geom_aoi, False)) == 2


def test_make_path_generates_string():
    """
    Test that the make_path function returns a string, and that it generates
    paths properly
    """
    assert type(utils.make_path("folder", "filename")) is str