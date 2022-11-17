import ee
import geemap

from eeharvest import msg


def initialise(auth_mode="gcloud"):
    """
    Initialise Google Earth Engine API

    Try to initialise Google Earth Engine API. If it fails, the user is prompted
    to authenticate through the command line interface.
    """
    # Check if initialised:
    if ee.data._credentials:
        msg.warn("Earth Engine API already authenticated")
    else:
        with msg.spin("Initialising Earth Engine...") as s:
            geemap.ee_initialize(auth_mode=auth_mode)
            s()
        if ee.data._credentials:
            msg.success("Earth Engine authenticated")
        else:
            msg.warn(
                "Something went wrong, please run `initialise()` again to authenticate"
            )
