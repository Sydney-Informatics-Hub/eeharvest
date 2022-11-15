import datetime  # for date parsing, but check later if this is needed

import ee
import geemap.colormaps as cm
import geemap.foliumap as geemap
import yaml
from termcolor import cprint

from eeharvest import msg, utils


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
    date : str
        Start date of image(s) to be collected in YYYY-MM-DD or YYYY format
    end_date : str, optional
        End date of image(s) to be collected in YYYY-MM-DD or YYYY format
    buffer : int, optional
        If `coords` is a point, a buffer can be provided to create a polygon.
        The buffer is in metres
    bound : bool, optional
        Instead of a circular buffer, request a square bounding box around the
        point based on the buffer size
    config: str
        Path string to a YAML configuration file. A default configuration file
        can be generated for editing using `template()` method.

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
        # Stop if minimum requirements are not met
        if config is None and any(a is None for a in [collection, coords, date_min]):
            raise ValueError(
                "Missing required argument(s): collection, coords, date_min"
            )
        elif config is not None:
            # Open and aggregate configuration settings into groups
            with open(config, "r") as f:
                # TODO: put into kwargs at some point to clean this up
                yaml_vals = yaml.load(f, Loader=yaml.SafeLoader)

            # Parse settings
            gee_config = yaml_vals["target_sources"]["GEE"]
            gee_process = gee_config["preprocess"]
            try:
                gee_aggregate = gee_config["aggregate"]
            except KeyError:
                pass
            gee_download = gee_config["download"]

            # Class attributes:
            collection = gee_process["collection"]
            if coords is not None:
                coords = gee_process["coords"]

            # If date and endate are provided, overwrite everything
            try:
                gee_process["date"]
            except KeyError:
                gee_process["date"] = None
            try:
                gee_process["end_date"]
            except KeyError:
                gee_process["end_date"] = None
            use_gee_dates = False
            if gee_process["date"] is not None and gee_process["end_date"] is not None:
                date_min = gee_process["date"]
                date_max = gee_process["end_date"]
                use_gee_dates = True
            elif gee_process["date"] is not None and gee_process["end_date"] is None:
                # start = str(date[0]) + "-01-01"
                # end_date = str(date[0]) + "-12-31"
                # year_to_range = parse_year_to_range(gee_process["date"])
                date_min = str(gee_process["date"][0]) + "-01-01"
                date_max = str(gee_process["date"][0]) + "-12-31"
                use_gee_dates = True

            if use_gee_dates is False:
                if len(yaml_vals["target_dates"]) == 1:
                    pass
                elif len(yaml_vals["target_dates"]) > 1:
                    print("Multiple dates provided, using first date for GEE")

                date_min = str(yaml_vals["target_dates"][0]) + "-01-01"
                date_max = str(yaml_vals["target_dates"][0]) + "-12-31"

            # Set GEE preprocessing attributes to None if not found so that the script
            # doesn't crash
            try:
                gee_process["buffer"]
            except KeyError:
                gee_process["buffer"] = None
            try:
                gee_process["bound"]
            except KeyError:
                gee_process["bound"] = None

            # check dates
            if isinstance(date_min, datetime.date):
                date_min = date_min.strftime("%Y-%m-%d")
            if isinstance(date_max, datetime.date):
                date_max = date_max.strftime("%Y-%m-%d")
            # Ok, store method-specific settings
            self.yaml_vals = yaml_vals
            self.gee_config = gee_config
            self.gee_process = gee_process
            try:
                self.gee_aggregate = gee_aggregate
            except Exception:
                pass
            self.gee_download = gee_download

        # check that collection exists in GEE catalog
        valid = utils.validate_collection(collection)

        # Finalise
        self.collection = collection
        self.coords = coords
        self.date = str(date_min)
        self.end_date = str(date_max)
        self.buffer = buffer
        self.bound = bound

        # Used for checks:
        if config is not None:
            self.hasconfig = True
        else:
            self.hasconfig = False
        self.ee_image = None
        self.scale = None
        self.minmax = None
        self.image_count = 1
        self.valid = valid

    def preprocess(
        self,
        mask_clouds=True,
        reduce="median",
        spectral=None,
        clip=True,
        **kwargs,
    ):
        """
        Preprocess an Earth Engine Image or ImageCollection

        Obtain image stacks from a Google Earth Engine catalog collection for
        processing. Full support for Sentinel-2, Landsat 5-8, Soil and Landscape
        Grid Australia (CSIRO) and DEM (Geoscience Australia). Preprocessing
        performs server-side filtering, cloud masking, scaling and offsetting,
        calculation of spectral indices and compositing into a single image
        representing, for example, the median, min, max, mean, quantile or
        standard deviation of the images.

        Parameters
        ----------
        mask_clouds : bool, optional
            Performs cloud and shadow masking for Sentinel-2 and Landsat 5-9
            image collections, by default True
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
        msg.info("Running preprocess()")
        # Check if user has provided a config file
        if self.hasconfig is True:
            mask_clouds = self.gee_process["mask_clouds"]
            reduce = self.gee_process["reduce"]
            spectral = self.gee_process["spectral"]
        # Generate area of interest
        if len(self.coords) == 4:
            aoi = ee.Geometry.Rectangle(self.coords)
        elif len(self.coords) == 2:
            aoi = ee.Geometry.Point(self.coords)
        # Is there a buffer? Is a point supplied? Then buffer it
        if self.buffer is not None and len(self.coords) == 2:
            aoi = aoi.buffer(self.buffer)
        if self.bound is True and self.buffer is not None:
            aoi = aoi.bounds()
        # Filter dates
        img = ee.ImageCollection(self.collection).filterBounds(aoi)
        img = img.filterDate(self.date, self.end_date)
        # Check if there are any images by verifying that image bands exist
        # NOT WORKING
        try:
            img.first().bandNames().getInfo()
        except ee.EEException:
            cprint(
                "✘ No images - please verify date range. Processing cancelled",
                "red",
                attrs=["bold"],
            )
        # Count images if reduce is None:
        if reduce is False or reduce is None:
            reduce = None
            with msg.spin("Image collection requested, counting images...") as s:
                image_count = int(img.size().getInfo())
                if image_count > 0:
                    self.image_count = image_count  # store for later use
                else:
                    cprint("✘ No images found, please check date range", "red")
                    return None
                s(1)
        # Scale and offset, mask clouds
        try:
            img = img.scaleAndOffset()
        except Exception:
            pass
        if mask_clouds:
            try:
                with msg.spin("Applying scale, offset and cloud masks...") as s:
                    img = img.maskClouds()
                    s(1)
            except Exception:
                pass
        # Spectral index
        if spectral is not None:
            with msg.spin(f"Computing spectral index: {spectral}") as s:
                try:
                    # Validation: check if spectral index is supported
                    full_list = list(utils.get_indices().keys())
                    spectral_list = (
                        [spectral] if isinstance(spectral, str) else spectral
                    )
                    if not set(spectral_list).issubset(full_list):
                        raise Exception(
                            cprint(
                                "✘ At least one of your spectral indices is not valid. "
                                "Please check the list of available indices at "
                                "https://awesome-ee-spectral-indices.readthedocs.io"
                                " Processing cancelled",
                                "red",
                                attrs=["bold"],
                            )
                        )
                    img = img.spectralIndices(spectral, online=True)
                except Exception:
                    pass
                s(1)
        else:
            pass
        # Function to map to collection

        def clip_collection(image):
            return image.clip(aoi)

        if clip:
            img = img.map(clip_collection)
        # If image is an image collection, limit to 3 samples for stretching pixels
        ee_sample = img.limit(3)
        # Reduce/aggregate
        reducers = ["median", "mean", "sum", "mode", "max", "min", "mosaic"]
        if reduce is None:
            msg.info(f"Selected {image_count} image(s) without aggregation")
        elif reduce in reducers:
            with msg.spin(f"Reducing image pixels by {reduce}") as s:
                func = getattr(img, reduce)
                img = func()
                s(1)
        # Update metadata (TODO: perhaps a better way to do this)
        self.aoi = aoi
        self.reduce = reduce
        self.spectral = spectral
        self.ee_sample = ee_sample
        self.ee_image = img
        msg.success("Google Earth Engine preprocessing complete")
        return img

    def aggregate(self, frequency="month", reduce_by=None, **kwargs):
        """
        Aggregate an Earth Engine Image or ImageCollection by period

        Parameters
        ----------
        frequency : str, optional
            aggregation frequency, either by "day". "week" or "month", by
            default "month"
        """
        msg.info("Running aggregate()")
        if reduce_by is None:
            reducer = ee.Reducer.mean()
        # Check if user has provided a config file
        if self.hasconfig is True:
            frequency = self.gee_aggregate["frequency"]
            reduce_by = self.gee_aggregate["reduce_by"]
            cprint(f"Using ee.Reducer.{reduce_by}", "yellow")
        img = self.ee_image
        # Convert to wxee object
        ts = img.wx.to_time_series()
        cprint("\u2139 Initial aggregate", "blue")
        ts.describe()
        out = ts.aggregate_time(frequency=frequency, reducer=reducer)
        with msg.spin("Calculating new temporal aggregate...") as s:
            out.describe()
            s(1)
        self.ee_image = out

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
        msg.info("Running map()")
        # Check that preprocess() has been called
        img = self.ee_image
        if img is None:
            print("✘ No image found, please run `preprocess()` before mapping")
            return None
        # Validate that at least one band is selected
        all_bands = utils.get_bandinfo(img)
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
        if self.aoi.getInfo()["type"] == "Point":
            msg.warn(
                "Looks like geometry is set to a single point with "
                + "no buffer. Plotting anyway..."
            )
        # Create min and max parameters for map
        if minmax is None:
            with msg.spin("Detecting band min and max parameters...") as s:
                # Scale here is just for visualisation purposes
                if len(bands) == 1:
                    minmax = utils.stretch_minmax(
                        self.ee_sample, self.aoi, bands, by="sd", scale=100
                    )
                elif len(bands) > 1:
                    minmax = utils.stretch_minmax(
                        self.ee_sample, self.aoi, bands, by="sd", scale=100
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
                Map.add_time_slider(img, param, time_interval=3)
                # Map.add_colorbar_branca(paramvis, label=bands[0],
                #     transparent_bg=False)
        # Otherwise, generate map without palette
        else:
            if isinstance(img, ee.image.Image):
                Map.addLayer(img, param, name=str(bands).strip("[]"))
            else:
                Map.add_time_slider(img, param, time_interval=3)
        # Add bounding box
        # Map.addLayer(self.aoi, shown=False)
        # Update class attributes
        self.bands = bands
        self.param = param
        self.minmax = minmax
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
        out_format=None,
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
        out_format : str, optional
            One of the following strings: "png", "jpg", "tif". If set to None,
            will use "tif", by default None
        overwrite : boolean, optional
            Overwrite existing file if it already exists, by default False

        Returns
        -------
        None
            Nothing is returned.

        Raises
        ------
        ValueError
            If out_format is not one of 'png', 'jpg', 'tif'.
        """
        msg.info("Running download()")
        # Check if user has provided a config file
        if self.hasconfig is True:
            bands = self.gee_download["bands"]
            scale = self.gee_download["scale"]
            outpath = self.yaml_vals["outpath"]
            out_format = self.gee_download["format"]
            overwrite = self.gee_download["overwrite"]
        # Check that preprocess() has been called
        img = self.ee_image
        if img is None:
            msg.err("No image found, please run `preprocess()` before mapping")
            return None
        # Stop if image is a pixel
        if self.aoi.getInfo()["type"] == "Point":
            msg.warn("Single pixel selected. Did you set a buffer in `collect()`?")
            msg.err("Download cancelled")
            return
        # Stop if out_format is not png, jpg or tif
        if out_format is None:
            # cprint(
            #     "• `out_format` is set to None, downloading as GEOTIFF, 'tif'", "blue"
            # )
            out_format = "tif"
        elif out_format not in ["png", "jpg", "tif"]:
            raise ValueError("out_format must be one of 'png', 'jpg' or 'tif'")
        # Validate that at least one band is selected
        if bands is None:
            try:
                bands = self.bands
            except AttributeError:
                all_bands = utils.get_bandinfo(img)
                msg.err("No bands defined")
                msg.info("Please select one or more bands to download image:")
                print(all_bands)
                return None
        img = img.select(bands)
        msg.info(f"Band(s) selected: {bands}")
        # Throw error if scale is None, i.e. force user to set scale again
        if scale is None:
            msg.warn("Scale not set, using scale=100")
            scale = 100
        # Determine save path
        if outpath is None:
            outpath = utils.generate_dir("downloads")
        else:
            outpath = utils.generate_dir(outpath)
        pathstring = utils.generate_path_string(
            img,
            self.collection,
            self.date,
            self.end_date,
            bands,
            self.reduce,
            scale,
            out_format,
        )
        fullpath = utils.make_path(outpath, pathstring)
        # Download file(s)
        is_tif = out_format.replace(".", "").lower() in ["tif", "tiff"]
        # cprint(f"• Downloading to {outpath}...", "blue")
        if is_tif:
            filenames = utils.download_tif(img, self.aoi, fullpath, scale, overwrite)
            self.filenames = filenames
        self.outpath = outpath
        msg.success("Google Earth Engine download(s) complete")
        return None


def byconfig(obj, **kwargs):
    """
    Preprocess, aggregate and download Earth Engine assets by config file
    """
    # TODO: Validate that config file is present
    if obj.hasconfig is False:
        raise Exception("This function requires a config file supplied in `collect()`")
    # Replace coordinates if needed
    if kwargs["coords"] is not None:
        obj.coords = kwargs["coords"]
    obj.preprocess()
    # try:
    #     obj.aggregate()
    # except Exception as e:
    #     print(e)
    obj.download()
    return obj
