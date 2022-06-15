import logging
import os
import re
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import rsm.db as rsm_db
import rsm.excel as rsm_excel
import yaml
from openpyxl.worksheet.worksheet import Worksheet
from rsm.utils import fmt_date
from rsm.utils import log_setup
from rsm.utils import parser_cfg


def template_config(loglevel):
    """
    Dumps example yaml config file to stdout
    """
    log_setup(loglevel)
    print(parser_cfg(None))


def validate(input, config, loglevel) -> Tuple[Dict[str, Any], Worksheet, datetime, Dict[str, int]]:
    log_setup(loglevel)
    input = os.path.abspath(input)
    config = os.path.abspath(config)
    logging.debug(f"Reading yaml file: {config}")
    str_config = parser_cfg(config)
    logging.debug(f"Loading yaml to object")
    yml_conf = yaml.safe_load(str_config)
    logging.debug(f"Validating xlsx")
    ws, monthly_dt, col_map = rsm_excel.validate_xlsx(input, yml_conf)
    logging.info("Files validated successfully")
    return (yml_conf, ws, monthly_dt, col_map)


def convert(input: str, config: str, output: str, loglevel: str) -> Tuple[Dict[str, Any], List[List[Any]]]:
    if output is None:
        output = re.sub(".xlsx$", ".csv", input)
    input = os.path.abspath(input)
    config = os.path.abspath(config)
    output = os.path.abspath(output)
    yml_conf, ws, monthly_dt, col_map = validate(input, config, loglevel)
    output_order = yml_conf["output_order"]
    data_store = []  # datastore has no header
    # -sig is to force the BOM (Byte Order Marker) at the start of the file
    with open(output, mode="w", encoding="utf-8-sig") as ofh:
        # header
        print(",".join(output_order), file=ofh)
        for r in range(3, ws.max_row + 1):
            if ws.cell(r, 1).value == "TOTALS":
                break
            row = [fmt_date(yml_conf["monthly_observation_sets"]["transform_csv"], monthly_dt)]
            for col in output_order:
                if col == "activity_month":
                    continue
                val = ws.cell(r, col_map[col]).value
                if val is None:
                    val = ""
                row.append(str(val))
            print(",".join(row), file=ofh)
            # now output update the date format so we don't need to run an update on the DB
            row[0] = fmt_date(yml_conf["monthly_observation_sets"]["transform_sql"], monthly_dt)
            # and add to the data store
            data_store.append(row)
    logging.info(f"Converted file written to: {output}")

    return (yml_conf, data_store)


def convert_to_db(input: str, config: str, output: str, loglevel: str):
    yml_conf, db_rows = convert(input, config, output, loglevel)
    rsm_db.upload(yml_conf, db_rows)
