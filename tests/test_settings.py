from eeharvest import settings


def test_read_config_works_and_can_be_indexed():
    """Test that the config file can be read"""
    # configfile = files("eeharvest.data").joinpath("template.yaml")
    configfile = "configs/template.yaml"
    config = settings.read(configfile)
    assert config is not None  # config exists
    assert config["colname_lat"] == "Lat"  # config can be indexed


def test_validate_schema_validates_error_free_file_with_schema_file(capsys, data_path):
    """
    validate_schema: should validate a config file with a schema file
    """
    configfile = data_path.joinpath("template.yaml")
    schemafile = data_path.joinpath("schema.yaml")
    settings.validate_schema(configfile, schemafile)
    captured = capsys.readouterr()
    assert "validated" in captured.out
