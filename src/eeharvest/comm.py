"""Functions for communicating with the user"""

import logging

from termcolor import cprint

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    filename="harvest.txt",
    filemode="w",
)


def msg_info(message, icon=True, log=False):
    """Prints an info message"""
    if log:
        logging.info(message)
    if icon:
        cprint("\u2139 " + message, color="magenta")
    else:
        cprint("  " + message, color="magenta")
