from importlib.resources import files

import yamale
import yaml

from eeharvest import msg


def read(path, loader=yaml.FullLoader):
    """Read the yaml config file"""
    with open(path, "r") as f:
        doc = yaml.load(f, Loader=loader)
    return doc


def validate_schema(path, schema_path=None):
    """Validate a yaml config file against a schema file"""
    if schema_path is None:
        schema_path = files("eeharvest.data").joinpath("schema.yaml")
    schema = yamale.make_schema(schema_path)
    try:
        data = yamale.make_data(path)
    except (FileNotFoundError, TypeError):
        path = yaml.dump(path)
        data = yamale.make_data(content=str(path))
    try:
        yamale.validate(schema, data)
        msg.success("YAML schema validated 👍")
    except yamale.YamaleError as e:
        for result in e.results:
            msg.err("Error validating YAML config")
            for error in result.errors:
                msg.info(f"\t{error}")
