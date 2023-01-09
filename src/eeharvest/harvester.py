# import datetime  # for date parsing, but check later if this is needed
import os

import ee
import eemont  # trunk-ignore(flake8/F401)
import geemap.colormaps as cm
import geemap.foliumap as geemap

from eeharvest import arc2meter, msg, settings, utils


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
            cfg = settings.read(config)
            settings.validate_schema(config)
            # TODO: below is probably not needed if we use dict.get()
            cfg = settings.add_missing_keys(cfg)
            self.config = cfg
            return
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
        mask_probability=60,
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
            coords = cfg["target_bbox"]
            date_min = cfg["date_min"]
            date_max = cfg["date_max"]
            buffer = gee_cfg["buffer"]
            bound = gee_cfg["bound"]
            mask_clouds = gee_cfg["mask_clouds"]
            reduce = gee_cfg["reduce"]
            spectral = gee_cfg["spectral"]
        # Let's start ----------------------------------------------------------
        # Define the collection, and filter by aoi
        aoi = ee.Geometry.Rectangle(coords)
        img = (
            ee.ImageCollection(collection)
            .filterBounds(aoi)
            .filterDate(str(date_min), str(date_max))
        )
        # Cloud and shadow masking
        if mask_clouds:
            with msg.spin("Applying scale, offset and cloud masks...") as s:
                img = img.scaleAndOffset().maskClouds(prob=mask_probability)
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
        reducers = ["median", "mean", "sum", "mode", "max", "min", "mosaic"]
        if reduce is None:
            msg.info("Skipping image reduction")
        elif reduce in reducers:
            with msg.spin(f"Reducing image pixels by {reduce}") as s:
                func = getattr(img, reduce)
                img = func()
                s(1)
        else:
            raise ValueError(
                f"Reducer {reduce} not supported, please use one of {reducers}"
            )
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
        else:
            pass
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
        # Check config file
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
            if outpath is not None:
                pass
            elif cfg["outpath"] is not None:
                outpath = cfg["outpath"]
            else:
                outpath = os.path.join(os.getcwd(), "downloads")
        else:
            collection = self.collection
            date_min = self.date_min
            date_max = self.date_max
        # These should already be stored in the class
        try:
            img = self.ee_image
        except AttributeError:
            msg.err("No image found, please run `preprocess()` before downloading")
        aoi = self.aoi
        reduce = self.reduce
        # Check if bands are set
        if bands is None:
            all_bands = utils.get_bandinfo(img)
            msg.err("No bands defined")
            msg.info("Please select one or more bands to download image:")
            msg.info(str(all_bands))
            return
        else:
            img = img.select(bands)
            msg.info(f"Band(s) selected: {bands}")

        # Convert scale from arsec to meters (if from config file)
        if cfg is None:
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
        hash = utils._generate_hash(
            collection, date_min, date_max, bands, reduce, scale
        )
        filename = f"ee_{''.join(collection.split('/')[0])}_{hash}.tif"

        # Generate path string
        final_destination = os.path.join(utils._generate_dir(outpath), filename)
        msg.info(f"Setting download dir to {outpath}")
        filenames = utils.download_tif(
            img, aoi, final_destination, scale, overwrite=overwrite
        )
        msg.success("Google Earth Engine download(s) complete")
        # Housekeeping
        self.filenames = filenames
        return img


def auto(config, outpath=None):
    """Run all steps of the GEE download process when a configuration YAML file
    is supplied."""
    img = collect(config=config)
    img.preprocess()
    if outpath is None:
        img.download()
    else:
        img.download(outpath=outpath)
    return img
