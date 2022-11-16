import logging

from alive_progress import alive_bar, config_handler
from termcolor import colored, cprint

# Define alive_progress config
config_handler.set_global(
    force_tty=True,
    bar=None,
    spinner="waves",
    monitor=False,
    stats=False,
    receipt=True,
    elapsed="{elapsed}",
)


def info(message, icon=True, log=False):
    """Prints a custom info message"""
    if log:
        logging.info(message)
    if icon:
        cprint("\u2139 " + message.lstrip(), color="magenta")
    else:
        cprint("  " + message.lstrip(), color="magenta")


def title(message, log=False):
    """Prints a custom title message"""
    if log:
        logging.info(message)
        # u25cc?
    cprint(message + " -----", color="cyan", attrs=["bold"])


def dl(message, log=False):
    """Prints a custom downloading message"""
    if log:
        logging.info(message)
    cprint("\u29e9 " + message, color="magenta")


def warn(message, log=False):
    """Prints a custom warning message"""
    if log:
        logging.warning(message)
    cprint("\u2691 " + message, color="red")


def err(message, log=False):
    """Prints a custom error message"""
    if log:
        logging.error(message)
    cprint("\u2716 " + message.lstrip(), color="red", attrs=["bold"])


def success(message, log=False):
    """Prints a custom success message"""
    if log:
        logging.info(message)
    cprint("\u2714 " + message, color="green")


def spin(message=None, colour="magenta", events=1, log=False):
    """Spin animation as a progress inidicator"""
    if log:
        logging.info(message)
    return alive_bar(events, title=colored("\u2299 " + message, color=colour))
