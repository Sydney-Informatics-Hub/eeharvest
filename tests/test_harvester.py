# trunk-ignore(flake8/F401)
import eemont
import pytest

from eeharvest import auth, harvester

# def test_collect_produces_ValueError_when_minimum_args_not_provided():
#     with pytest.raises(ValueError) as excinfo:
#         harvester.collect(
#             collection="LANDSAT/LC08/C02/T1_L2",
#             coords=[149.799, -30.31, 149.80, -30.309],
#         )
#     assert "Missing" in str(excinfo.value)
#     with pytest.raises(ValueError) as excinfo:
#         harvester.collect(
#             collection="LANDSAT/LC08/C02/T1_L2",
#             date_min="2019-01-01",
#         )
#     assert "Missing" in str(excinfo.value)
#     with pytest.raises(ValueError) as excinfo:
#         harvester.collect(
#             coords=[149.799, -30.31, 149.80, -30.309],
#             date_min="2019-01-01",
#         )
#     assert "Missing" in str(excinfo.value)


def test_collect_stops_when_minimum_args_not_provided(capsys):
    """
    The collect class method should stop when minimum args are not provided.
    These args are: collection, coords, date_min.
    """
    auth.initialise()
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
    auth.initialise()
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
    auth.initialise()
    assert to_harvest.collection == "LANDSAT/LC08/C02/T1_L2"
    assert to_harvest.coords == [149.799, -30.31, 149.80, -30.309]
    assert to_harvest.date_min == "2019-01-01"
    assert to_harvest.date_max == "2019-02-01"


def test_preprocess(to_harvest):
    auth.initialise()
    to_harvest.preprocess(mask_clouds=True, reduce="median", spectral=None, clip=True)
    assert to_harvest.reduce == "median"
    assert to_harvest.spectral is None

    to_harvest.preprocess(mask_clouds=False, reduce=None, spectral="NDVI", clip=False)
    assert to_harvest.spectral == "NDVI"


def test_map(capsys, to_harvest):
    """collect.map: should not produce errors"""
    auth.initialise()
    to_harvest.preprocess(mask_clouds=True, reduce="median", spectral="NDVI", clip=True)
    to_harvest.map(bands="NDVI")
    captured = capsys.readouterr()
    assert "Map generated" in captured.out

    to_harvest.map(bands=None)
    captured = capsys.readouterr()
    assert "nothing to preview" in captured.out

    to_harvest.map(bands="NDVI", palette="ndvi")
    captured = capsys.readouterr()
    assert "Map generated" in captured.out

    with pytest.raises(ValueError) as excinfo:
        to_harvest.preprocess(reduce="monkey")
    assert "not supported" in str(excinfo.value)


def test_map_works_with_imagecollection(capsys, to_harvest):
    """collect.map: should work with multiple image in an ImageCollection"""
    auth.initialise()
    to_harvest.preprocess(mask_clouds=True, reduce=None, spectral="NDVI", clip=True)
    to_harvest.map(bands="NDVI")
    captured = capsys.readouterr()
    assert "previewing first image only" in captured.out


def test_config_works_with_harvester_module(tmp_path):
    """collect: should work with a config file supplied"""
    auth.initialise()
    img = harvester.collect(config="tests/data/template.yaml")
    assert type(img.config) is dict

    img.preprocess()
    assert img.reduce == "median"

    img.download(outpath=tmp_path)
    tif_exists = False
    for root, dirs, files in os.walk(tmp_path):
        for file in files:
            if file.endswith(".tif"):
                tif_exists = True
    assert tif_exists is True


def test_map_requires_preprocess_to_run_first(to_harvest):
    """map: will not produce image if preprocess() has not been run"""
    with pytest.raises(AttributeError) as excinfo:
        to_harvest.map(bands=["B1", "B2", "B3"])
    assert "No image found" in str(excinfo.value)
