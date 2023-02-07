import pandas as pd
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
        # msg.success("YAML schema validated")
        return True
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


def _validate_bbox(d, buffer=0.05):
    """Checks whether a bounding box can be parsed from infile or target_bbox"""
    if d["infile"] is not None:
        # Extract csv from infile using pandas
        try:
            df = pd.read_csv(d["infile"])
        except (FileNotFoundError, ValueError):
            msg.err("Invalid file path, please check `infile` value in config")
            raise ValueError("Could not read csv file")
    else:
        pass

    # Check if target_bbox is defined
    if d["target_bbox"] is not None:
        bbox = d["target_bbox"]
        return bbox
    if any(val is None for val in [d["infile"], d["colname_lng"], d["colname_lat"]]):
        msg.err(
            "If target_bbox is not defined, infile, colname_lng and"
            + " colname_lat must be defined"
        )
        raise ValueError(
            "Cannot parse bounding box from `infile` and `target_bbox` is None."
            " Please check config file for issues or typos in these keys."
        )
    else:
        long = d["colname_lng"]
        lat = d["colname_lat"]
        bbox = (
            min(df[long]) - buffer,
            min(df[lat]) - buffer,
            max(df[long]) + buffer,
            max(df[lat]) + buffer,
        )
        return bbox


def _detect_multi_collection(config):
    """
    Detects whether multiple collections are specified in the config file.

    If True, there are multiple collections.
    """
    if isinstance(config["target_sources"]["GEE"]["preprocess"]["collection"], list):
        if len(config["target_sources"]["GEE"]["preprocess"]["collection"]) > 1:
            return True
        else:
            return False
    else:
        return False
