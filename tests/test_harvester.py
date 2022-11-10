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
