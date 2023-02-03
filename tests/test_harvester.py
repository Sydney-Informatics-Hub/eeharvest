import os
import os.path

# trunk-ignore(flake8/F401)
import eemont
import pytest

from eeharvest import harvester, settings


def test_collect_stops_when_minimum_args_not_provided(capsys):
    """
    The collect class method should stop when minimum args are not provided.
    These args are: collection, coords, date_min.
    """
    harvester.collect(
        collection="LANDSAT/LC08/C02/T1_L2",
        coords=[149.799, -30.31, 149.80, -30.309],
    )
    captured = capsys.readouterr()
    assert "not met" in captured.out
    harvester.collect(
        collection="LANDSAT/LC08/C02/T1_L2",
        date_min="2019-01-01",
    )
    captured = capsys.readouterr()
    assert "not met" in captured.out
    harvester.collect(
        coords=[149.799, -30.31, 149.80, -30.309],
        date_min="2019-01-01",
    )
    captured = capsys.readouterr()
    assert "not met" in captured.out


def test_collect_works_with_minimum_args_provided():
    """
    The collect class method should work when minimum args are provided.
    These args are: collection, coords, date_min.
    """
    try:
        img = harvester.collect(
            collection="LANDSAT/LC08/C02/T1_L2",
            coords=[149.799, -30.31, 149.80, -30.309],
            date_min="2019-01-01",
        )
    except Exception as e:
        assert False, f"'collect' raised an exception {e}"
    assert img.collection == "LANDSAT/LC08/C02/T1_L2"


def test_collect_indexing_works(to_harvest):
    """
    Once the collect class method is called, the class should be indexable
    for the following attributes: collection, coords, date_min, date_max
    """
    assert to_harvest.collection == "LANDSAT/LC08/C02/T1_L2"
    assert to_harvest.coords == [149.799, -30.31, 149.80, -30.309]
    assert to_harvest.date_min == "2019-01-01"
    assert to_harvest.date_max == "2019-02-01"


def test_preprocess(to_harvest):
    to_harvest.preprocess(mask_clouds=True, reduce="median", spectral=None, clip=True)
    assert to_harvest.reduce == "median"
    assert to_harvest.spectral is None

    to_harvest.preprocess(mask_clouds=False, reduce=None, spectral="NDVI", clip=False)
    assert to_harvest.spectral == "NDVI"


def test_map_basically_works(capsys, to_harvest):
    """collect.map: should not produce errors"""
    to_harvest.preprocess(spectral="NDVI")
    to_harvest.map(bands="NDVI_median")
    captured = capsys.readouterr()
    assert "Map generated" in captured.out

    to_harvest.map(bands=None)
    captured = capsys.readouterr()
    assert "nothing to preview" in captured.out


def test_map_accepts_certain_palette_values(capsys, to_harvest):
    to_harvest.preprocess(spectral="NDVI")
    to_harvest.map(bands="NDVI_median", palette="ndvi")
    captured = capsys.readouterr()
    assert "Map generated" in captured.out

    to_harvest.map(bands="NDVI_median", palette="ndwi")
    captured = capsys.readouterr()
    assert "Map generated" in captured.out

    to_harvest.map(bands="NDVI_median", palette="terrain")
    captured = capsys.readouterr()
    assert "Map generated" in captured.out


def test_preprocess_produces_error_when_reduce_value_is_not_supported(to_harvest):
    with pytest.raises(AttributeError) as excinfo:
        to_harvest.preprocess(reduce="monkey")
    assert "has no attribute" in str(excinfo.value)


def test_map_saves_html_to_folder_if_specified(to_harvest, tmp_path):
    harvester.initialise()
    to_harvest.preprocess(mask_clouds=True, reduce="median", spectral="NDVI", clip=True)
    to_harvest.map(
        bands="NDVI_median", save_to=os.path.join(str(tmp_path), "test.html")
    )


def test_map_works_with_imagecollection(capsys, to_harvest):
    """collect.map: should work with multiple image in an ImageCollection"""
    harvester.initialise()
    to_harvest.preprocess(mask_clouds=True, reduce=None, spectral="NDVI", clip=True)
    to_harvest.map(bands="NDVI")
    captured = capsys.readouterr()
    assert "previewing first image only" in captured.out


def test_config_works_with_harvester_module(tmp_path):
    """collect: should work with a config file supplied"""
    harvester.initialise()
    img = harvester.collect(config="tests/data/template.yaml")
    assert type(img.config) is dict

    img.preprocess()
    assert img.reduce == "median"

    # img.download(outpath=tmp_path)
    # tif_exists = False
    # for root, dirs, files in os.walk(tmp_path):
    #     for file in files:
    #         if file.endswith(".tif"):
    #             tif_exists = True
    # assert tif_exists is True


def test_map_requires_preprocess_to_run_first():
    """map: will not produce image if preprocess() has not been run"""
    img = harvester.collect(
        collection="LANDSAT/LC08/C02/T1_L2",
        coords=[149.799, -30.31, 149.80, -30.309],
        date_min="2019-01-01",
        date_max="2019-02-01",
    )
    with pytest.raises(AttributeError) as excinfo:
        img.map(bands=["SR_B1", "SR_B2", "SR_B3"])
    assert "No image found" in str(excinfo.value)


def test_auto_just_works(tmp_path):
    img = harvester.auto(config="tests/data/template.yaml", outpath=tmp_path)
    assert type(img) is harvester.collect

    tif_exists = False
    for root, dirs, files in os.walk(tmp_path):
        for file in files:
            if file.endswith(".tif"):
                tif_exists = True
    assert tif_exists is True


def test_auto_can_handle_multiple_collections(tmp_path):
    img = harvester.auto(config="tests/data/multi.yaml", outpath=tmp_path)

    tif_exists = False
    for root, dirs, files in os.walk(tmp_path):
        for file in files:
            if file.endswith(".tif"):
                tif_exists = True
    assert tif_exists is True


def test_auto_validates_bands_poperly():
    with pytest.raises(ValueError) as excinfo:
        img = harvester.auto(config="tests/data/multi_bad_band.yaml")
    assert "Invalid bands" in str(excinfo.value)


def test_download_returns_None_if_no_bands_provided(capsys, to_harvest):
    to_harvest.preprocess()
    to_harvest.download(bands=None)
    captured = capsys.readouterr()
    assert "No bands" in captured.out


def test_collect_accepts_config_dict():
    cfg = settings.read("tests/data/template.yaml")
    img = harvester.collect(config=cfg)
    assert type(img.config) is dict


def test_preprocess_stops_if_zero_images_found_in_image_collection():
    img = harvester.collect(
        collection="LANDSAT/LC08/C02/T1_L2",
        coords=[149.799, -30.31, 149.80, -30.309],
        date_min="2019-01-01",
        date_max="2019-01-02",
    )
    with pytest.raises(ValueError) as excinfo:
        img.preprocess()
    assert "No image to process" in str(excinfo.value)
