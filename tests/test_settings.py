import pytest
import yaml

from eeharvest import settings


def test_read_config_works_and_can_be_indexed():
    """Test that the config file can be read"""
    # configfile = files("eeharvest.data").joinpath("template.yaml")
    configfile = "tests/data/template.yaml"
    config = settings.read(configfile)
    assert config is not None  # config exists
    assert config["colname_lat"] == "Lat"  # config can be indexed


def test_validate_schema_validates_error_free_file_with_schema_file():
    """
    validate_schema: should validate a config file with a schema file
    """
    configfile = "tests/data/template.yaml"
    schemafile = "tests/data/schema.yaml"
    assert settings.validate_schema(configfile, schemafile) is True


def test_validate_schema_validates_string_with_schema_file():
    """
    validate_schema: should validate a string with a schema file and properly
    identify an error when a wrong key is provided
    """
    raw = """
target_res: 6
date_min: 2022-10-01
target_sources:
  GEE:
    preprocess:
      collection: LANDSAT/LC09/C02/T1_L2
      mask_clouds: True
      reduce: median
    download:
      hands: NDVI
    """
    configfile = yaml.load(raw, Loader=yaml.FullLoader)
    schemafile = "tests/data/schema.yaml"
    with pytest.raises(ValueError) as excinfo:
        settings.validate_schema(configfile, schemafile)
    assert "Error validating" in str(excinfo.value)


# def test_validate_schema_can_identify_incorrect_key_value(capsys, data_path):
#     """
#     Test that an error is raised when there when an incorrect key value is used
#     in the config file
#     """
#     raw = """
# target_res: 6
# date_min: 2022-10-01
# target_sources:
#   GEE:
#     preprocess:
#       collection: LANDSAT/LC09/C02/T1_L2
#       mask_clouds: True
#       reduce: median
#     download:
#       bands: null
#     """
#     configfile = yaml.load(raw, Loader=yaml.FullLoader)
#     schemafile = data_path.joinpath("schema.yaml")
#     settings.validate_schema(configfile, schemafile)
#     captured = capsys.readouterr()
#     assert "'None' is not a str" in captured.out


def test_add_missing_keys(data_path):
    configfile = data_path.joinpath("template.yaml")
    config = settings.read(configfile)
    newconfig = settings._add_missing_keys(config)

    assert newconfig["target_sources"]["GEE"]["preprocess"]["buffer"] is None
    assert newconfig["target_sources"]["GEE"]["preprocess"]["bound"] is None
