import logging
from datetime import datetime

from pkg_resources import require
from pkg_resources import resource_string

MY_VERSION = require(__name__.split(".")[0])[0].version


def version():
    return MY_VERSION


def log_setup(loglevel):
    logging.basicConfig(level=getattr(logging, loglevel.upper()), format="%(levelname)s: %(message)s")


def parser_cfg(user_defined: str) -> str:
    if user_defined:
        logging.debug("Loading parser config from user defined file")
        with open(user_defined, "r") as file:
            parser_cfg = file.read()
    else:
        logging.debug("Loading parser config from package resources")
        parser_cfg = resource_string(__name__, f"resources/parser.cfg.yaml").decode("utf-8", "strict")
    return parser_cfg


def fmt_date(fmt: str, value: datetime) -> str:
    """
    Function to cope with need to support ^ to force upper on month which isn't native on windows
    """
    if "^" in fmt:
        fmt = fmt.replace("^", "")
        new_value = value.strftime(fmt).upper()
    else:
        new_value = value.strftime(fmt)
    return new_value
