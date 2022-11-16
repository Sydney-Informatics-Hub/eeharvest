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


def add_missing_keys(config):
    """Check that the config file has the correct keys and add the keys with
    valeus of None if they are missing"""
    skeleton = {
        "infile": None,
        "outpath": None,
        "colname_lat": None,
        "colname_lng": None,
        "target_bbox": None,
        "target_res": None,
        "date_min": None,
        "date_max": None,
        "target_sources": {
            "GEE": {
                "preprocess": {
                    "collection": None,
                    "buffer": None,
                    "bound": None,
                    "mask_clouds": None,
                    "mask_probability": None,
                    "reduce": None,
                    "spectral": None,
                },
                "download": {"bands": None},
            }
        },
    }

    def merge(child, parent):
        """For a config file, fill in blanks with defaults"""

        d = {}
        for k in set().union(parent, child):
            if (
                k in child
                and isinstance(child[k], dict)
                and isinstance(parent[k], dict)
            ):
                v = merge(child[k], parent[k])
            elif k in child:
                v = child[k]
            else:
                v = parent[k]
            d[k] = v
        return d

    return merge(config, skeleton)
