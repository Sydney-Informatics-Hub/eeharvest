from eeharvest import settings


def test_read_config_works_and_can_be_indexed():
    """Test that the config file can be read"""
    # configfile = files("eeharvest.data").joinpath("template.yaml")
    configfile = "configs/template.yaml"
    config = settings.read(configfile)
    assert config is not None  # config exists
    assert config["colname_lat"] == "Lat"  # config can be indexed


def test_validate_schema_works_on_yaml(capsys):
    """Test that the config file can be validated against a schema"""
    settings.validate_schema("configs/template.yaml")
    captured = capsys.readouterr()
    assert "validated" in captured.out
