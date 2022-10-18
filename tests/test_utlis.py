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
