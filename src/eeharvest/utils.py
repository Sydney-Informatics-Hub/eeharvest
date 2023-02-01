import hashlib
import math
import os
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from os import devnull

import ee


@contextmanager
def _suppress():
    """
    A context manager that redirects stdout and stderr to devnull

    From https://stackoverflow.com/a/52442331.
    """
    with open(devnull, "w") as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
            yield (err, out)


def _imageID_to_tifID(collection):
    """
    Extracts the image IDs from an Earth Engine image collection and returns the
    IDs as a list of filenames in .tif
    """
    idList = collection.aggregate_array("system:index")
    return [f"{i}.tif" for i in idList.getInfo()]


def _stretch_minmax(
    ee_image, region, bands, by="percentile", percentile=98, sd=3, scale=None
):
    """
    Calculate min and max values for each band in an image

    Use percentile or standard deviation to generate minimum and maxmimum
    values for Earth Engine image band(s). Useful for visualisation.

    Parameters
    ----------
    ee_image : obj
        Earth Engine image object
    region : obj
        Earth Engine geometry object
    bands : str or list of str
        Band(s) to calculate min and max values for
    by : str, optional
        method to use to calculate min and max values, by default "percentile"
    percentile : int, optional
        Percentile to use to calculate min and max values, by default 98
    sd : int, optional
        Standard deviation to use to calculate min and max values, by default 3
    scale : int, optional
        Scale to use to calculate min and max values, by default None

    Returns
    -------
    list
        A list of min and max values for each band
    """
    try:
        ee_image = ee_image.median()
    except AttributeError:
        pass

    # Filter image to selected bands
    if by == "percentile":
        # Calculate start and end percentiles
        startp = 50 - (percentile / 2)
        endp = 50 + (percentile / 2)

        if not bands:
            names = ee_image.bandNames()
            bands = ee.List(
                ee.Algorithms.If(names.size().gte(3), names.slice(0, 3), names.slice(0))
            )
            bands = bands.getInfo()

        image = ee_image.select(bands)
        geom = region or image.geometry()
        params = dict(geometry=geom, bestEffort=True)
        # Set scale if available
        if scale:
            params["scale"] = scale
        params["reducer"] = ee.Reducer.percentile([startp, endp])
        percentiles = image.reduceRegion(**params)

        def minmax(band):
            minkey = ee.String(band).cat("_p").cat(ee.Number(startp).format())
            maxkey = ee.String(band).cat("_p").cat(ee.Number(endp).format())

            minv = ee.Number(percentiles.get(minkey))
            maxv = ee.Number(percentiles.get(maxkey))
            return ee.List([minv, maxv])

        if len(bands) == 1:
            band = bands[0]
            values = minmax(band).getInfo()
            minv = values[0]
            maxv = values[1]
        else:
            values = ee.List(bands).map(minmax).getInfo()
            minv = [values[0][0], values[1][0], values[2][0]]
            maxv = [values[0][1], values[1][1], values[2][1]]
    if by == "sd":
        ee_image = ee_image.select(bands)
        # Create dictionary
        geom = region or ee_image.geometry()
        params = dict(geometry=geom, bestEffort=True)
        # Set scale if available
        if scale:
            params["scale"] = scale
        params["reducer"] = ee.Reducer.mean()
        mean = ee_image.reduceRegion(**params)
        params["reducer"] = ee.Reducer.stdDev()
        stdDev = ee_image.reduceRegion(**params)

        def min_max(band, val):
            minv = ee.Number(val).subtract(ee.Number(stdDev.get(band)).multiply(sd))
            maxv = ee.Number(val).add(ee.Number(stdDev.get(band)).multiply(sd))
            return ee.List([minv, maxv])

        # Make calculations based on no. of bands used
        if len(bands) == 1:
            band = bands[0]
            values = min_max(band, mean.get(band)).getInfo()
            minv = values[0]
            maxv = values[1]
        else:
            values = mean.map(min_max).select(bands).getInfo()
            minv = [values[bands[0]][0], values[bands[1]][0], values[bands[2]][0]]
            maxv = [values[bands[0]][1], values[bands[1]][1], values[bands[2]][1]]
    return [minv, maxv]


def _generate_hash(*args):
    fullstring = "".join(map(str, args))
    return hashlib.shake_128(fullstring.encode()).hexdigest(4)


def _make_path(dir, filename):
    """
    Create full path to a file
    """
    if dir is None:
        path = filename
        pass
    elif filename is None:
        path = dir
        pass
    else:
        path = os.path.join(dir, filename)
    return path


# def generate_path_string(
#     ee_image,
#     name,
#     date,
#     end_date=None,
#     bands=None,
#     reduce=None,
#     scale=None,
#     ext="tif",
# ):
#     """
#     Generate a string to name a file or folder for Earth Engine downloads
#     """
#     # Clean colletion string
#     name = "".join(name.split("/")[0])
#     # Generate date string
#     try:
#         date = date.replace("-", "")
#     except (AttributeError, TypeError):
#         pass
#     try:
#         end_date = end_date.replace("-", "")
#     except (AttributeError, TypeError):
#         pass
#     # Generate band string
#     if bands is not None:
#         bands = "".join(str(i) for i in bands)
#         bands = bands.replace("_", "")
#     if scale is not None:
#         scale = "".join([str(scale), "m"])
#     if reduce is None:
#         reduce = ""
#     # The only difference is whether to add extension to string, or not
#     if isinstance(ee_image, ee.image.Image):
#         out = (
#             "_".join(filter(None, ["ee", name, date, end_date, bands, reduce, scale]))
#             + "."
#             + ext
#         )
#     else:
#         out = "_".join(filter(None, [name, date, end_date, bands, reduce, scale]))

#     return out


def _generate_dir(dir):
    """
    Create directory with subfolder if it doesn't exist
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


# def pixels_to_bytes(ee_image, scale):
#     """
#     Convert image pixel information to bytes for size estimation. From
#     https://gis.stackexchange.com/a/433027

#     Parameters
#     ----------
#     ee_image : ee.Image object
#         An ee.Image object
#     scale : int
#         The scale of the image in meters

#     Returns
#     -------
#     float
#         Size of image in bytes
#     """
#     imageDescription = ee.Dictionary(ee.Algorithms.Describe(ee_image))
#     bands = ee.List(imageDescription.get("bands"))

#     def getBits(band):
#         dataType = ee.Dictionary(ee.Dictionary(band).get("data_type"))
#         precision = dataType.getString("precision")
#         out = ee.Algorithms.If(
#             precision.equals("int"),
#             intBits(dataType),
#             ee.Algorithms.If(precision.equals("float"), 32, 64),
#         )
#         return out

#     def intBits(dataType):
#         min = dataType.getNumber("min")
#         max = dataType.getNumber("max")
#         types = ee.FeatureCollection(
#             [
#                 ee.Feature(None, {"bits": 8, "min": -(2**7), "max": 2**7}),
#                 ee.Feature(None, {"bits": 8, "min": 0, "max": 2**8}),
#                 ee.Feature(
#                     None,
#                     {
#                         "bits": 16,
#                         "min": -(2**5),
#                         "max": 2**5,
#                     },
#                 ),
#                 ee.Feature(None, {"bits": 16, "min": 0, "max": 2**16}),
#                 ee.Feature(
#                     None,
#                     {
#                         "bits": 32,
#                         "min": -(2**31),
#                         "max": 2**31,
#                     },
#                 ),
#                 ee.Feature(None, {"bits": 32, "min": 0, "max": 2**32}),
#             ]
#         )
#         out = (
#             types.filter(ee.Filter.lte("min", min))
#             .filter(ee.Filter.gt("max", max))
#             .merge(ee.FeatureCollection([ee.Feature(None, {"bits": 64})]))
#             .first()
#             .getNumber("bits")
#         )
#         return out

#     bits = ee.Number(bands.map(getBits).reduce(ee.Reducer.sum()))
#     pixelCount = (
#         ee_image.geometry()
#         .bounds()
#         .area(scale)
#         .divide(ee.Number(scale).pow(2))
#         .sqrt()
#         .ceil()
#         .pow(2)
#     )
#     return bits.divide(8).multiply(pixelCount).ceil()


def convert_size(size_bytes):
    """
    Convert size in bytes to appropriate unit.

    Source https://stackoverflow.com/a/14822210
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


# def parse_year_to_range(date):
#     """Convert single-year value to ymd range for the same year"""
#     start = str(date[0]) + "-01-01"
#     end_date = str(date[0]) + "-12-31"
#     return start, end_date


def _reduce_by_string(img, by="median"):
    """Reduce an ee.ImageCollection to a single ee.Image by evaluating a string"""
    if by.find("(") != -1:
        fun = "img.reduce(ee.Reducer." + by + ")"
    else:
        fun = "img.reduce(ee.Reducer." + by + "())"
    return eval(fun)


def _update_nested(source, *new_mappings):
    updated_source = source.copy()
    for new_map in new_mappings:
        for k, v in new_map.items():
            if (
                k in updated_source
                and isinstance(updated_source[k], dict)
                and isinstance(v, dict)
            ):
                updated_source[k] = _update_nested(updated_source[k], v)
            else:
                updated_source[k] = v
    return updated_source
