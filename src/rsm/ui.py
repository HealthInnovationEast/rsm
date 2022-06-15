import logging
import sys
from functools import wraps

import click
import rsm.constants as rsm_const
import rsm.main as rsm_main
from click_option_group import OptionGroup
from rsm.utils import version


def _file_exists():
    return click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    )


optgroup_debug = OptionGroup("\nDebug options", help="Options specific to troubleshooting, testing")


def debug_opts(f):
    @optgroup_debug.option(
        "-l",
        "--loglevel",
        required=False,
        default="INFO",
        show_default=True,
        type=click.Choice(rsm_const.LOG_LEVELS, case_sensitive=False),
        help="Set logging verbosity",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def parse_opts(f):
    @click.option(
        "-i",
        "--input",
        required=True,
        type=_file_exists(),
        help="xlsx input file",
    )
    @click.option(
        "-c",
        "--config",
        required=False,
        type=_file_exists(),
        help="YAML config for xlsx parsing, uses default when not defined",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def output_opts(f):
    @optgroup_debug.option(
        "-o",
        "--output",
        required=False,
        type=str,
        help="File to write csv output to [default: input with csv extension]",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


@click.group()
@click.version_option(version())
def cli():
    pass


@cli.command()
@parse_opts
@debug_opts
def validate_xlsx(*args, **kwargs):
    """
    Validate the provided xlsx file vs yaml config.
    """
    rsm_main.validate(*args, **kwargs)


@cli.command()
@parse_opts
@output_opts
@debug_opts
def to_csv(*args, **kwargs):
    """
    Convert the provided xlsx file to csv using the yaml config.
    """
    rsm_main.convert(*args, **kwargs)


@cli.command()
@parse_opts
@output_opts
@debug_opts
def to_db(*args, **kwargs):
    """
    Convert the provided xlsx file to csv and load into database.

    Requires "connection" section of `parser.cfg.yaml` to be completed, password will be requested interactively.
    """
    rsm_main.convert_to_db(*args, **kwargs)


@cli.command()
@debug_opts
def template_config(*args, **kwargs):
    """
    Dumps example yaml config file to stdout
    """
    rsm_main.template_config(*args, **kwargs)
