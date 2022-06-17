"""Small utility functions."""
import logging
from datetime import datetime

from pkg_resources import require
from pkg_resources import resource_string

MY_VERSION = require(__name__.split(".")[0])[0].version


def version():
    """Access to version for comand line.

    Returns:
        str: Version string.
    """
    return MY_VERSION


def log_setup(loglevel):
    """Log setup."""
    logging.basicConfig(level=getattr(logging, loglevel.upper()), format="%(levelname)s: %(message)s")


def parser_cfg(user_defined: str) -> str:
    """Config file loader.

    Loads provided file or the default config file.

    Args:
        user_defined (str): Path to user defined config file (optional)

    Returns:
        str: File or internal resource loaded into string.
    """
    if user_defined:
        logging.debug("Loading parser config from user defined file")
        with open(user_defined, "r") as file:
            parser_cfg = file.read()
    else:
        logging.debug("Loading parser config from package resources")
        parser_cfg = resource_string(__name__, f"resources/parser.cfg.yaml").decode("utf-8", "strict")
    return parser_cfg


def fmt_date(fmt: str, value: datetime) -> str:
    """Handle lack of POSIX date formats.

    Needed to support ^ to force upper on month which isn't native on windows.

    Args:
        fmt (str): A POSIX date format.
        value (datetime): Date to be formated.

    Returns:
        str: Formatted date.
    """
    if "^" in fmt:
        fmt = fmt.replace("^", "")
        new_value = value.strftime(fmt).upper()
    else:
        new_value = value.strftime(fmt)
    return new_value
