# At some point, check
# https://gis.stackexchange.com/questions/377222/creating-automated-tests-using-google-earth-engine-python-api
import sys

# https://stackoverflow.com/a/67246674


def test_that_repeat_authentication_is_not_required(capsys):
    """Test that repeat authentication is not required."""
    for key in list(sys.modules.keys()):
        if key.startswith("eeharvest"):
            del sys.modules[key]
    from eeharvest import harvester

    harvester.initialise()
    captured = capsys.readouterr()
    assert "authenticated" in captured.out
    harvester.initialise()
    captured = capsys.readouterr()
    assert "already authenticated" in captured.out
