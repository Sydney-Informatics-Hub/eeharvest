# trunk-ignore(flake8/F401)
import eemont
import pytest

from eeharvest import harvester


def test_collect_produces_ValueError_when_minimum_args_not_provided():
    with pytest.raises(ValueError) as excinfo:
        harvester.collect(
            collection="LANDSAT/LC08/C02/T1_L2",
            coords=[149.799, -30.31, 149.80, -30.309],
        )
    assert "Missing" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        harvester.collect(
            collection="LANDSAT/LC08/C02/T1_L2",
            date_min="2019-01-01",
        )
    assert "Missing" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        harvester.collect(
            coords=[149.799, -30.31, 149.80, -30.309],
            date_min="2019-01-01",
        )
    assert "Missing" in str(excinfo.value)


def test_collect_works_with_minimum_args():
    try:
        harvester.collect(
            collection="LANDSAT/LC08/C02/T1_L2",
            coords=[149.799, -30.31, 149.80, -30.309],
            date_min="2019-01-01",
        )
    except Exception as e:
        assert False, f"'collect' raised an exception {e}"


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
