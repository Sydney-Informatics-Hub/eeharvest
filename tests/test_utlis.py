import os

import pytest

from eeharvest import harvester, utils


def test_suppress_stdout(capsys):
    """Test the suppress_stdout function"""
    with utils._suppress():
        print("This should not be printed")
    captured = capsys.readouterr()
    assert "This should not be printed" not in captured.out


def test_get_indices():
    """
    Test that the get_indices function downloads the list of indices from
    Awesome Spectral Indices and prints them as a dict
    """
    assert type(harvester.get_indices()) is dict


def test_imageID_to_tifID(ee_imagecollection):
    """
    Test that the imageID_to_tifID function extracts image IDs from an
    ee.ImageCollection and returns a list of names in .tif format
    """
    assert type(utils._imageID_to_tifID(ee_imagecollection)) is list


def test_validate_collection():
    """
    Test that the validate_collection function returns True if the collection
    is valid and False if it is not
    """
    assert harvester.validate_collection("LANDSAT/LC08/C02/T1_L2") is True
    assert harvester.validate_collection("MODIS/006/MCD43A4") is True
    assert harvester.validate_collection("NOT/A/COLLECTION") is False


def test_get_bandinfo(ee_image):
    """
    Test that the get_bandinfo function returns a list of band names when run
    on an ee.ImageCollection or ee.Image object
    """
    bands = harvester.get_bandinfo(ee_image)
    assert type(bands) is list


def test_stretch_minmax_accepts_3_bands(ee_image, geom_aoi):
    """
    stretch_minmax: function returns a list of length 2 when three bands are
    provided, and that it accepts the 'by' argument
    """
    assert (
        len(
            utils._stretch_minmax(
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
            utils._stretch_minmax(
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
    assert len(utils._stretch_minmax(ee_image, geom_aoi, ["SR_B1"], scale=100)) == 2
    assert len(utils._stretch_minmax(ee_image, geom_aoi, ["SR_B1"], "sd")) == 2


def test_stretch_minmax_produces_exception_if_not_1_or_3_bands_provided(
    ee_image, geom_aoi
):
    """
    stretch_minmax: function raises an exception if not 1 or 3 bands are
    provided
    """
    # Raise error if two bands are provided
    with pytest.raises(IndexError) as excinfo:
        utils._stretch_minmax(ee_image, geom_aoi, ["SR_B1", "SR_B2"])
    assert "list index out of range" in str(excinfo.value)


def test_stretch_minmax_accepts_None_for_bands_argument(ee_image, geom_aoi):
    """
    :stretch_minmax: function accepts False for the bands argument
    """
    # No bands provided i.e. bands=False
    assert len(utils._stretch_minmax(ee_image, geom_aoi, False)) == 2


def test_make_path_generates_string():
    """
    Test that the make_path function returns a string, and that it generates
    paths properly
    """
    assert type(utils._make_path("folder", "filename")) is str


def test_make_path_generates_proper_pathnames():
    assert utils._make_path("folder", "filename") == "folder/filename"
    assert utils._make_path(None, "filename") == "filename"
    assert utils._make_path("folder", None) == "folder"


# def test_generate_path_string(ee_image):
#     """
#     Test that the generate_path_string function returns a string, and that it
#     generates paths properly
#     """
#     path = utils.generate_path_string(
#         ee_image=ee_image,
#         name="test",
#         date="20221011",
#         bands=["B1", "B2"],
#         reduce="mean",
#         scale="100",
#     )
#     assert type(path) is str
#     assert path == "ee_tes_20221011_B1B2_mean_100m.tif"

#     path = utils.generate_path_string(
#         ee_image=ee_image,
#         name="test",
#         date="20221011",
#         bands=None,
#         reduce=None,
#         scale=None,
#     )
#     assert type(path) is str
#     assert path == "ee_tes_20221011.tif"


def test_generate_dir(tmpdir):
    """
    Test that the generate_dir function creates a directory if it does not
    exist, and returns the path to the directory
    """
    mydir = tmpdir.mkdir("monkey")
    dir1 = utils._generate_dir(str(mydir))
    # dir2 = utils._generate_dir(str(mydir), "data")
    assert type(dir1) is str
    # assert type(dir2) is str
    assert "monkey" in dir1
    # assert "monkey/data" in dir2


def test_download_tif_single_image(tmpdir, ee_image, coords, capsys):
    """Test that the download_tif function downloads a single tif file"""
    # Generate a temporary directory
    mydir = tmpdir.mkdir("download")
    mypath = os.path.join(mydir + ".tif")
    # Download file
    harvester.download_tif(image=ee_image, region=coords, path=mypath, scale=100)
    assert os.path.isfile(mypath) is True
    # Skip if file has already been downloaded
    harvester.download_tif(image=ee_image, region=coords, path=mypath, scale=100)
    captured = capsys.readouterr()
    assert "already exists" in captured.out


def test_download_tif_multiple_images(tmpdir, ee_imagecollection, coords):
    """
    Test that the download_tif function downloads multiple tif files. In this
    instance, two files should be downloaded.
    """
    # Generate a temporary directory
    mydir = tmpdir.mkdir("download")
    # Download files
    harvester.download_tif(
        image=ee_imagecollection, region=coords, path=mydir, scale=100
    )
    count = 0
    for path in os.scandir(mydir):
        if path.is_file():
            count += 1
    assert count == 2
