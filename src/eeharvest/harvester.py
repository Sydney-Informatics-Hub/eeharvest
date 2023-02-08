# import datetime  # for date parsing, but check later if this is needed
import base64
import json
import os
import urllib
from functools import partialmethod

import ee
import eemont  # trunk-ignore(flake8/F401)
import geemap.colormaps as cm
import geemap.foliumap as geemap
from tqdm.notebook import tqdm

from eeharvest import arc2meter, msg, settings, utils


def initialise(token_name="EARTHENGINE_TOKEN", auth_mode="gcloud"):
    """
    Initialise Google Earth Engine API

    Try to initialise Google Earth Engine API. If it fails, the user is prompted
    to authenticate through the command line interface.

    Now accepts service tokens as well for use with testing and CI/CD.
    """
    with msg.spin("Initialising Earth Engine...") as s:
        if ee.data._credentials is None:
            try:
                token = os.environ[token_name]
                if token is not None:
                    content = base64.b64decode(token).decode()
                    with open("ee_private_key.json", "w") as f:
                        f.write(content)
                    service_account = "my-service-account@...gserviceaccount.com"
                    credentials = ee.ServiceAccountCredentials(
                        service_account, "ee_private_key.json"
                    )
                    ee.Initialize(credentials)
            except Exception:
                geemap.ee_initialize(auth_mode)
        s()
    msg.success("Done")


# def initialise(token_name="EARTHENGINE_TOKEN", auth_mode="gcloud"):
#     """
#     Initialise Google Earth Engine API

#     Try to initialise Google Earth Engine API. If it fails, the user is prompted
#     to authenticate through the command line interface.
#     """
#     # Check if initialised:
#     if "EARTHENGINE_TOKEN" in os.environ:
#         # key need to be decoded in a file to work
#         content = base64.b64decode(os.environ["EARTHENGINE_TOKEN"]).decode()
#         with open("ee_private_key.json", "w") as f:
#             f.write(content)

#         # connection to the service account
#         service_account = "my-service-account@...gserviceaccount.com"
#         credentials = ee.ServiceAccountCredentials(
#             service_account, "ee_private_key.json"
#         )
#         ee.Initialize(credentials)
#     else:
#         if ee.data._credentials:
#             msg.warn("Earth Engine API already authenticated")
#         else:
#             with msg.spin("Initialising Earth Engine...") as s:
#                 try:
#                     geemap.ee_initialize(auth_mode=auth_mode)
#                 except Exception as e:
#                     print(e)
#                 s()
#             if ee.data._credentials:
#                 msg.success("Earth Engine authenticated")
#             else:
#                 msg.warn("Initialisation cancelled. Please check error message")


# For the people in USA :|
initialize = initialise


class collect:
    """
    A class to manipulate Google Earth Engine objects

    This class brings additional packages into the mix to manipulate Earth
    Engine objects, specifically images.

    Attributes
    ----------
    collection: str
        A Google Earth Engine collection. Collections can be found on
        https://developers.google.com/earth-engine/datasets
    coords: list of str
        GPS coordinates in WGS84 [East, North]. Minimum of one set of
        coordinates should be provided to create a point coordinate. If more
        than one set of coordinates is provided, a polygon will be created
        Start date of image(s) to be collected in YYYY-MM-DD or YYYY format
    date_max : str, optional
        End date of image(s) to be collected in YYYY-MM-DD or YYYY format
    buffer : int, optional
        If `coords` is a point, a buffer can be provided to create a polygon.
        The buffer is in metres
    bound : bool, optional
        Instead of a circular buffer, request a square bounding box around the
        point based on the buffer size
    config: str
        Path string to a YAML configuration file. A default configuration file
        can be generated for editing using `template()` method

    Methods
    -------
    preprocess():
        filter, mask, buffer, reduce and/or clip an image collection
    aggregate():
        perform temporal aggregation on an image collection
    map():
        preview an image or image collection
    download():
        download an image or image collection in tif, png or csv format
    """

    def __init__(
        self,
        collection=None,
        coords=None,
        date_min=None,
        date_max=None,
        buffer=None,
        bound=False,
        config=None,
    ):
        # Check if config is a path to a file or a dictionary and read it
        if config is not None:
            try:
                cfg = settings.read(config)
            except TypeError:
                if type(config) is dict:
                    cfg = config
                else:
                    raise TypeError("`config` should be a path or a dictionary")
            settings.validate_schema(config)
            cfg = settings._add_missing_keys(cfg)
            self.config = cfg
            # validate bounding box from config
            coords = settings._validate_bbox(cfg)
            cfg.update({"target_bbox": coords})
        else:
            self.config = None
            # check minimum requirements: if collection, coords, date_min are
            # not None, pass, otherwise print the argument that is missing
            if all(v is not None for v in [collection, coords, date_min]):
                pass
            else:
                msg.err("Minimum required arguments are not met")
                if collection is None:
                    msg.info("'collection' should not be None")
                if coords is None:
                    msg.info("`coords` should not be None")
                if date_min is None:
                    msg.info("`date_min` should not be None")
            # Save into class attributes
            self.collection = collection
            self.coords = coords
            self.date_min = date_min
            self.date_max = date_max
            self.buffer = buffer
            self.bound = bound
        return

    def preprocess(
        self,
        mask_clouds=True,
        mask_probability=None,
        reduce="median",
        spectral=None,
        clip=True,
        **kwargs,
    ):
        """
        Preprocess an Earth Engine Image or ImageCollection

        Obtain image stacks from a Google Earth Engine catalog collection for
        processing. Preprocessing performs server-side filtering, cloud masking,
        scaling and offsetting, calculation of spectral indices and compositing
        into a single image representing, for example, the median, min, max,
        mean, quantile or standard deviation of the images.

        Parameters
        ----------
        mask_clouds : bool, optional
            Performs cloud and shadow masking for Sentinel-2 and Landsat 5-9
            image collections, by default True
        mask_probability: int, optional
            The probability threshold for cloud masking. This is only used if
            cloud masking is enabled, by default 60
        reduce : str, optional
            Composite or reduce an image collection into a single image. A
            comprehensive list of reducers can be viewed from the "ee.Reducer"
            section of the Earth Engine API which also documents their use
            (https://developers.google.com/earth-engine/apidocs/). The most
            common reducers are "min", "max", "minMax", "median", "mean",
            "mode", "stDev" and "percentile",  by default "median"
        spectral : list of str, optional
            Calculate one or more spectral indices via Awesome Spectral Indices
            (https://awesome-ee-spectral-indices.readthedocs.io/en/latest/).
            This is performed automatically by applying the expressions defined
            on the website, by default None
        clip : bool, optional
            Clip the image. This only affects the interactive map view and will
            not influence the data download, by default True

        Returns
        -------
        ee.Image.Image or ee.Image.ImageCollection
            An Earth Engine object which can be further manipulated should the
            user not choose to use other methods in the class.
        """
        msg.title("Running preprocess()")
        # Check if user has provided a config file
        if self.config is None:
            collection = self.collection
            coords = self.coords
            date_min = self.date_min
            date_max = self.date_max
            buffer = self.buffer
            bound = self.bound
        else:
            # Extract settings from config
            cfg = self.config
            gee_cfg = cfg["target_sources"]["GEE"]["preprocess"]
            collection = gee_cfg["collection"]
            if type(collection) is list and len(collection) > 1:
                msg.err(
                    "cannot process more than one collection at a time, "
                    "perhaps you meant to use `auto()`? Please check configuration YAML "
                    "and make sure that `collection` is a string and not a list"
                )
                raise TypeError("can only process one collection at a time")
            coords = cfg["target_bbox"]
            date_min = cfg["date_min"]
            date_max = cfg["date_max"]
            buffer = gee_cfg["buffer"]
            bound = gee_cfg["bound"]
            mask_clouds = gee_cfg["mask_clouds"]
            reduce = gee_cfg["reduce"]
            spectral = gee_cfg["spectral"]
        # Make sure collection is a string
        if isinstance(collection, list) and len(collection) == 1:
            collection = collection[0]
        # Let's start ----------------------------------------------------------
        # Define the collection, and filter by aoi
        aoi = ee.Geometry.Rectangle(coords)
        img = (
            ee.ImageCollection(collection)
            .filterBounds(aoi)
            .filterDate(str(date_min), str(date_max))
        )
        # How many images?
        count = img.size()
        msg.info(f"Number of image(s) found: {count.getInfo()}")

        # Stop if no images found
        if count.getInfo() < 1:
            msg.err("Can't process zero images. Processing stopped")
            raise ValueError("No image to process, check your date range")

        # Cloud and shadow masking
        if mask_clouds:
            with msg.spin("Applying scale, offset and cloud masks...") as s:
                if mask_probability is None:
                    mask_probability = 60
                img.scaleAndOffset().maskClouds(prob=mask_probability)
                s(1)
        # Calculate spectral indices
        if spectral is not None:
            with msg.spin(f"Calculating spectral indices: {spectral}...") as s:
                img = img.spectralIndices(spectral, online=True)
                s(1)

        # Clip image to aoi
        if clip:

            def clip_all(image):
                return image.clip(aoi)

            img = img.map(clip_all)
        # Reduce image collection
        if reduce is not None:
            img = utils._reduce_by_string(img, reduce)
        # Store attributes
        self.ee_image = img
        self.collection = collection
        self.aoi = aoi
        self.reduce = reduce
        self.spectral = spectral

        msg.success("Preprocessing complete")
        return img

    # def aggregate(self, frequency="month", reduce_by=None, **kwargs):
    #     """
    #     Aggregate an Earth Engine Image or ImageCollection by period

    #     Parameters
    #     ----------
    #     frequency : str, optional
    #         aggregation frequency, either by "day". "week" or "month", by
    #         default "month"
    #     """
    #     msg.title("Running aggregate()")
    #     if reduce_by is None:
    #         reducer = ee.Reducer.mean()
    #     # Check if user has provided a config file
    #     if self.hasconfig is True:
    #         frequency = self.gee_aggregate["frequency"]
    #         reduce_by = self.gee_aggregate["reduce_by"]
    #         cprint(f"Using ee.Reducer.{reduce_by}", "yellow")
    #     img = self.ee_image
    #     # Convert to wxee object
    #     ts = img.wx.to_time_series()
    #     cprint("\u2139 Initial aggregate", "blue")
    #     ts.describe()
    #     out = ts.aggregate_time(frequency=frequency, reducer=reducer)
    #     with msg.spin("Calculating new temporal aggregate...") as s:
    #         out.describe()
    #         s(1)
    #     self.ee_image = out

    def map(self, bands=None, minmax=None, palette=None, save_to=None, **kwargs):
        """
        Visualise an Earth Engine Image or ImageCollection on a map

        Parameters
        ----------
        bands : str or list of str, optional
            A string or list of strings representing the bands to be visualised.
        minmax : list of int, optional
            A list of two integers representing the minimum and maximum values.
            If set to None, the min and max values are automatically calculated,
            by default None
        palette : str, optional
            A string representing the name of a palette to be used for map
            colors. Names are accessed from Matplotlib Colourmaps as described
            in https://matplotlib.org/stable/tutorials/colors/colormaps.html. In
            addition, "ndvi", "ndwi" and "terrain" palettes are available. If
            set to None, "viridis" is used, by default None
        save_to : str, optional
            A string representing the path to save the map to. If set to None,
            will not save the map, by default None

        Returns
        -------
        geemap.Map
            An interactive map object which can be further manipulated. A
            preview is also genereated.

        Raises
        ------
        ValueError
            If the bands are not valid or not present in the image.
        """
        msg.title("Running map()")
        # Check that preprocess() has been called
        try:
            img = self.ee_image
        except AttributeError:
            raise AttributeError("No image found, please run `preprocess()`")
        # Validate that at least one band is selected
        all_bands = get_bandinfo(img)
        if bands is None:
            print("✘ No bands defined - nothing to preview")
            print("\u2139 Please select one or more bands to view image:")
            print(all_bands)
            return None
        else:
            # Just making sure that bands is a list
            bands = [bands] if isinstance(bands, str) else bands
        if not set(bands).issubset(set(all_bands)):
            raise ValueError(
                f"Pattern '{bands}' not found in image. "
                + f"Available bands: {all_bands}"
            )
        # Initialise map
        # SLOW FOR TEMPORAL AGGREGATION, CHECK
        # Band(s) exist, let's filter
        bands = [bands] if isinstance(bands, str) else bands
        img = img.select(bands)
        # Check if geometry is a point and let user know
        # if self.aoi.getInfo()["type"] == "Point":
        #     msg.warn(
        #         "Looks like geometry is set to a single point with "
        #         + "no buffer. Plotting anyway..."
        #     )
        # Create min and max parameters for map
        if minmax is None:
            with msg.spin("Detecting band min and max parameters...") as s:
                # Scale here is just for visualisation purposes]
                minmax = utils._stretch_minmax(
                    self.ee_image, self.aoi, bands, by="sd", scale=100
                )
                s(1)
        param = dict(
            min=minmax[0],
            max=minmax[1],
        )
        Map = geemap.Map()
        # Generate palette if single-band
        if len(bands) == 1:
            if palette is None:
                msg.warn("Palette is set to None, using 'viridis'")
                palette = geemap.get_palette_colors("viridis")
            # add some custom palettes provided by geemap
            elif palette.lower() == "ndvi":
                palette = cm.palettes.ndvi
            elif palette.lower() == "ndwi":
                palette = cm.palettes.ndwi
            elif palette.lower() == "terrain":
                palette = cm.palettes.terrain
            # Generate map layer
            param.update(palette=palette)
            # param.update(region=self.aoi)
            if isinstance(img, ee.image.Image):
                Map.addLayer(img, param, name=bands[0])
            else:
                msg.info("Multiple images found, previewing first image only")
                Map.addLayer(img.first(), param, name=bands[0])
                # Map.add_time_slider(img, param, time_interval=3)
                # Map.add_colorbar_branca(paramvis, label=bands[0],
                #     transparent_bg=False)
        # Otherwise, generate map without palette
        else:
            if isinstance(img, ee.image.Image):
                Map.addLayer(img, param, name=str(bands).strip("[]"))
            else:
                msg.info("Multiple images found, previewing first image only")
                Map.addLayer(img.first(), param, name=str(bands).strip("[]"))
                # Map.add_time_slider(img, param, time_interval=3)
        # Add bounding box
        # Map.addLayer(self.aoi, shown=False)
        # Update class attributes
        self.param = param
        self.minmax = minmax  # for user if they want the values
        # For R preview to HTML
        if save_to is not None:
            # Save map html to temp directory
            Map.centerObject(self.aoi, 12)
            Map.to_html(save_to)
        Map.centerObject(self.aoi)
        msg.success("Map generated")
        return Map

    def download(
        self,
        bands=None,
        scale=None,
        outpath=None,
        overwrite=False,
        **kwargs,
    ):
        """
        Download an Earth Engine asset to disk and update logtable

        Parameters
        ----------
        bands : str or list of str, optional
            A string or list of strings representing the bands to be visualised.
            If set to None, will check if bands are set in the class. If not,
            the user will be prompted to select one or more bands, by default
            None
        scale : int, optional
            A number representing the scale of the image in meters. If set to
            None, will pick a default scale value of 100 m, by default None
        outpath : str, optional
            A string representing the path to the output directory. If set to
            None, will use the current working directory and add a "downloads"
            folder, by default None
        overwrite : boolean, optional
            Overwrite existing file if it already exists, by default False

        Returns
        -------
        img : ee.Image
            An Earth Engine image object

        Raises
        ------
        ValueError
            If out_format is not one of 'png', 'jpg', 'tif'.
        """
        msg.title("Running download()")
        # If a config file is set, extract settings from config
        if self.config is not None:
            # Extract settings from config
            cfg = self.config
            gee_cfg = cfg["target_sources"]["GEE"]
            collection = gee_cfg["preprocess"]["collection"]
            date_min = cfg["date_min"]
            date_max = cfg["date_max"]
            reduce = gee_cfg["preprocess"]["reduce"]
            coords = cfg["target_bbox"]
            bands = cfg["target_sources"]["GEE"]["download"]["bands"]
            scale = cfg["target_res"]
            # If outpath is None, check if it's set in the config. If not, use
            # default location of `downloads` folder in working directory
            if outpath is None:
                if cfg["outpath"] is not None:
                    outpath = cfg["outpath"]
                else:
                    outpath = "downloads"
        else:
            if outpath is None:
                outpath = "downloads"
            collection = self.collection
            date_min = self.date_min
            date_max = self.date_max
            if scale is None:
                scale = 100
        bands = [bands] if isinstance(bands, str) else bands
        # Make sure that preprocess has been run
        try:
            img = self.ee_image
        except AttributeError:
            msg.err("No image found, please run `preprocess()` before downloading")
        aoi = self.aoi
        reduce = self.reduce
        # Check if bands are set
        all_bands = get_bandinfo(img)
        if bands is None:
            msg.err("No bands defined")
            msg.info("Please select one or more bands to download image:")
            msg.info(str(all_bands))
            return
        else:
            # Match bands if they were modified by "reduce" in preprocess()
            new_bands = []
            for item in all_bands:
                for sub_item in bands:
                    if item.startswith(sub_item + "_"):
                        new_bands.append(item)
                        break
            img = img.select(new_bands)
            msg.info(f"Band(s) selected: {new_bands}")

        # Convert scale from arsec to meters (if from config file)
        if self.config is None:
            pass
        else:
            lat_center = (coords[1] + coords[3]) / 2
            xres_meters, yres_meters = arc2meter.calc_arc2meter(scale, lat_center)
            msg.info(
                f"Setting scale to ~{xres_meters:.1f}m, converted from "
                + f"{scale} arcsec at latitude {lat_center:.2f}"
            )
            scale = round(xres_meters, 1)

        # Use attributes to generate filename hash
        new_bands = [new_bands] if isinstance(new_bands, str) else new_bands
        # Make sure collection is a string
        if isinstance(collection, list) and len(collection) == 1:
            collection = collection[0]
        hash = utils._generate_hash(
            collection, date_min, date_max, new_bands, reduce, scale
        )
        filename = f"ee_{''.join(collection.split('/')[0])}_{hash}.tif"

        # Generate path string
        final_destination = os.path.join(utils._generate_dir(outpath), filename)
        msg.info(f"Setting download dir to {outpath}")
        filenames = download_tif(
            img, aoi, final_destination, scale, overwrite=overwrite
        )
        msg.success("Google Earth Engine download(s) complete")
        # Housekeeping
        self.filenames = filenames
        return img


class AutoResult:
    def __init__(self, obj, filenames):
        self.obj = obj
        self.filenames = [filenames] if isinstance(filenames, str) else filenames


def auto(config, outpath=None):
    cfg = settings.read(config)
    multi = settings._detect_multi_collection(cfg)
    if multi:
        collections = cfg["target_sources"]["GEE"]["preprocess"]["collection"]
        num_configs = len(collections)
        msg.info("Multiple collections detected in Google Earth Engine config file")
        msg.info(
            f"Validating settings and generating {num_configs} configuration profiles"
        )

        # Validate bands
        bands = cfg["target_sources"]["GEE"]["download"]["bands"]
        if all(isinstance(i, list) for i in bands):
            for (n, i, j) in zip(range(1, num_configs + 1), collections, bands):
                print(f"  Profile {n} will process '{i}' and download bands {j}")
        else:
            msg.err(
                "For each collection, you need to add a list of bands to download in a \n"
                "  list of lists e.g. [['B2', 'B3', 'B4'], ['SR_B1', 'SR_B2', 'SR_B3']]"
            )
            raise ValueError(
                "Invalid bands list, must be a list of lists if a list of image collections"
                " is provided"
            )

        # Generate new configs
        new_configs = []
        for (n, i, j) in zip(range(1, num_configs + 1), collections, bands):
            new_config = utils._update_nested(
                cfg, {"target_sources": {"GEE": {"preprocess": {"collection": i}}}}
            )
            new_config = utils._update_nested(
                new_config, {"target_sources": {"GEE": {"download": {"bands": j}}}}
            )
            new_configs.append(new_config)

        # Process and download
        img_list = []
        for (n, i) in zip(range(1, num_configs + 1), new_configs):
            msg.info(
                f"-------------------- Downloading Profile {n} --------------------"
            )
            img = collect(config=i)
            img.preprocess()
            img.download(outpath=outpath)
            img_list.append(img)
        filenames = [i.filenames for i in img_list]
        return AutoResult(img_list, filenames)
    else:
        # download single collection
        img = collect(config=config)
        img.preprocess()
        if outpath is None:
            img.download()
        else:
            img.download(outpath=outpath)
        filenames = img.filenames
        return AutoResult(img, filenames)


def get_indices() -> dict:
    """
    Returns a dictionary of available indices from Awesome Spectral Indices
    """
    with urllib.request.urlopen(
        # trunk-ignore(flake8/E501)
        "https://raw.githubusercontent.com/awesome-spectral-indices/awesome-spectral-indices/main/output/spectral-indices-dict.json"
    ) as url:
        try:
            indices = json.loads(url.read().decode())
        except Exception as e:
            print(e)
    return indices["SpectralIndices"]


def ee_stac():
    """
    Returns full list of STAC IDs from the Earth Engine Data Catalog
    """
    try:
        # trunk-ignore(flake8/E501)
        stac_url = "https://raw.githubusercontent.com/samapriya/Earth-Engine-Datasets-List/master/gee_catalog.json"
        datasets = []
        with urllib.request.urlopen(stac_url) as url:
            data = json.loads(url.read().decode())
            datasets = [item["id"] for item in data]
        return datasets
    except Exception as e:
        raise Exception(e)


def download_tif(image, region, path, scale, crs="EPSG:4326", overwrite=False):
    """
    Download image to local folder as GeoTIFF

    Parameters
    ----------
    image : obj
        ee.Image or ee.ImageCollection object
    region : dict
        ee.Geometry object
    path : str
        Path to save image to
    scale : int
        Scale in metres to define the image resolution
    crs : str, optional
        Coordinate reference system, by default "EPSG:4326"
    """
    if isinstance(image, ee.image.Image):
        filename = os.path.basename(path)
        # Check if path already exists and don't download if it does
        if os.path.exists(path) and overwrite is False:
            msg.warn(f"{filename} already exists, skipping download")
            return filename
        # Otherwise download image
        with utils._suppress():
            # hide tqdm if disable=True
            tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)
            # Get filename from path

            with msg.spin(f"Downloading {filename}") as s:
                geemap.download_ee_image(
                    image=image,
                    region=region,
                    filename=path,
                    crs="EPSG:4326",
                    scale=scale,
                )
                s(1)
        # final_size = convert_size(os.path.getsize(path))
        # cprint(f"✔ File saved as {path} [final size {final_size}]", "green")
        return filename
    else:
        file_list = utils._imageID_to_tifID(image)
        geemap.download_ee_image_collection(
            collection=image,
            out_dir=path,
            region=region,
            crs="EPSG:4326",
            scale=scale,
        )
        # cprint(f"✔ Files saved to {path}", "green")
    return file_list


def validate_collection(collection):
    """
    Checks whether collection ID string is a STAC in the GEE catalog

    Parameters
    ----------
    collection : string
        A string representing the collection ID

    Returns
    -------
    boolean
        True if collection is in the GEE catalog, False otherwise
    """
    stac_list = ee_stac()
    supported = supported_collections()
    # Check if collection is in STAC and supported
    if collection in stac_list and collection in list(supported.keys()):
        return True
    # If in STAC but not supported, print info and continue
    elif collection in stac_list and collection not in list(supported.keys()):
        msg.warn(f"Collection {collection} is not officially supported.")
        print("  Some preprocessing and aggregation steps are not available")
        return True
    else:
        errmsg = (
            f"Collection {collection} not found in GEE STAC. Please "
            + "check spelling or find a collection from "
            + "https://developers.google.com/earth-engine/datasets/catalog"
        )
        msg.err(errmsg)
        return False


def supported_collections():
    """
    A dictionary of supported collections
    """
    supported = {
        "LANDSAT/LT05/C02/T1_L2": "Landsat 5 TM Surface Reflectance",
        "LANDSAT/LE07/C02/T1_L2": "Landsat 7 ETM+ Surface Reflectance",
        "LANDSAT/LC08/C02/T1_L2": "Landsat 8 OLI/TIRS Surface Reflectance",
        "LANDSAT/LC09/C02/T1_L2": "Landsat 9 OLI-2/TIRS-2 Surface Reflectance",
        "COPERNICUS/S2_SR": "Sentinel-2 Surface Reflectance",
        "CSIRO/SLGA": "Soil and Landscape Grid of Australia (SLGA)",
    }
    return supported


def get_bandinfo(image):
    """
    Return list of available bands in image
    """
    try:
        bands = image.bandNames().getInfo()
    except AttributeError:
        bands = image.first().bandNames().getInfo()
    return bands
