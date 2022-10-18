import ee
import pytest

from eeharvest import utils


def test_suppress_stdout(capsys):
    """Test the suppress_stdout function"""
    with utils.suppress():
        print("This should not be printed")
    captured = capsys.readouterr()
    assert "This should not be printed" not in captured.out
