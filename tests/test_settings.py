from eeharvest import settings


def test_read_config_works_and_can_be_indexed():
    """Test that the config file can be read"""
    config = settings.read("configs/template.yaml")
    assert config is not None  # config exists
    assert config["colname_lat"] == "Lat"  # config can be indexed
