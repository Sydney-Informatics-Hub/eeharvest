import yamale
import yaml

from eeharvest import msg


def read(path, loader=yaml.FullLoader):
    """Read the yaml config file"""
    with open(path, "r") as f:
        doc = yaml.load(f, Loader=loader)
    return doc


def validate_schema(yaml):
    """Validate a yaml config file against a schema file"""
    schema = yamale.make_schema("../configs/schema.yaml")

    try:
        data = yamale.make_data(yaml)
    except (FileNotFoundError, TypeError):
        yaml = yaml.dump(yaml)
        data = yamale.make_data(content=str(yaml))
    try:
        yamale.validate(schema, data)
        msg.success("YAML schema validated 👍")
    except yamale.YamaleError as e:
        for result in e.results:
            print(f"Error validating {result.data}")
            for error in result.errors:
                msg.err("\t%s" % error)
