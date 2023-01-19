import yamale
import yaml
from importlib_resources import files

from eeharvest import msg


def read(path, loader=yaml.SafeLoader):
    """Read a yaml file and return a dict"""
    with open(path, "r") as f:
        doc = yaml.load(f, Loader=loader)
    return doc


def validate_schema(path, schema_path=None):
    """Validate a yaml config file against a schema file"""
    if schema_path is None:
        schema_path = files("eeharvest.data").joinpath("schema.yaml")
    schema = yamale.make_schema(str(schema_path))
    try:
        data = yamale.make_data(path)
    except (FileNotFoundError, TypeError):
        path = yaml.dump(path)
        data = yamale.make_data(content=str(path))
    try:
        yamale.validate(schema, data, strict=False)
        msg.success("YAML schema validated")
    except yamale.YamaleError as e:
        msg.err(f"{type(e).__name__}" + f"{e}")
        raise ValueError("Error validating config file against schema file")


def _add_missing_keys(config):
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

    def merge(d1, d2):
        for key in d2:
            if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
                merge(d1[key], d2[key])
            else:
                d1[key] = d2[key]
        return d1

    return merge(skeleton, config)
