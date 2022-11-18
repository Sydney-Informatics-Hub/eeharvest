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


def test_collect_indexing_works():
    img = harvester.collect(
        collection="LANDSAT/LC08/C02/T1_L2",
        coords=[149.799, -30.31, 149.80, -30.309],
        date_min="2019-01-01",
        date_max="2019-02-01",
    )
    assert img.collection == "LANDSAT/LC08/C02/T1_L2"
    assert img.coords == [149.799, -30.31, 149.80, -30.309]
    assert img.date_min == "2019-01-01"
    assert img.date_max == "2019-02-01"


def test_preprocess():
    img = harvester.collect(
        collection="LANDSAT/LC08/C02/T1_L2",
        coords=[149.799, -30.31, 149.80, -30.309],
        date_min="2019-01-01",
        date_max="2019-02-01",
    )
    img.preprocess(mask_clouds=True, reduce="median", spectral=None, clip=True)
    assert img.reduce == "median"
    assert img.spectral is None
    assert img.image_count == 1


def test_map(capsys):
    """collect.map: should not produce errors"""
    img = harvester.collect(
        collection="LANDSAT/LC08/C02/T1_L2",
        coords=[149.799, -30.31, 149.80, -30.309],
        date_min="2019-01-01",
        date_max="2019-02-01",
    )
    img.preprocess(mask_clouds=True, reduce="median", spectral="NDVI", clip=True)
    img.map(bands="NDVI")
    captured = capsys.readouterr()
    assert "Map generated" in captured.out
