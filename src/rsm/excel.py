import logging
import sys
from datetime import datetime
from typing import Dict
from typing import Tuple

from openpyxl import load_workbook
from openpyxl.cell.cell import Cell
from openpyxl.cell.cell import MergedCell
from openpyxl.worksheet.worksheet import Worksheet


def merged_range_end(ws: Worksheet, row: int, col_start: int, col_max: int) -> int:
    r_end = 0
    for i in range(col_start, col_max):
        c = ws.cell(row, i)
        c_t = type(c)
        if c_t == Cell:
            break
        if c_t == MergedCell:
            r_end = i

    return r_end


def ranges_in_row(ws: Worksheet, row: int, col_max: int) -> list[Tuple[int, int]]:
    ranges = []
    for i in range(1, col_max):
        c = ws.cell(row, i)
        if type(c) is MergedCell:
            continue
        r_start = i
        r_end = merged_range_end(ws, row, i + 1, col_max)
        if r_end > 0:
            ranges.append((r_start, r_end))
    return ranges


def core_cols(conf: dict, ws: Worksheet, core_stop: int) -> Dict[str, int]:
    row = 2
    col_map = {}
    core_set = conf["core_fields"]
    core_keys = core_set.keys()
    captured = 0
    for i in range(1, core_stop + 1):
        val = ws.cell(row, i).value.replace("\n", "").replace("\r", "")
        if val in core_keys:
            col_map[core_set[val]] = i
            captured += 1
    if captured != len(core_keys):
        logging.error(f"Expecting {len(core_keys)} core fields but only got got {captured}")
        logging.error(f" -> Expected: {', '.join(core_keys)}")
        sys.exit(1)
    return col_map


def monthly_cols(conf: dict, ws: Worksheet, monthly_range: tuple, col_map: dict) -> Dict[str, int]:
    row = 2
    monthly_set = conf["monthly_observations"]
    monthly_keys = monthly_set.keys()
    captured = 0
    for i in range(monthly_range[0], monthly_range[1] + 1):
        val = ws.cell(row, i).value.replace("\n", "").replace("\r", "")
        if val in monthly_keys:
            col_map[monthly_set[val]] = i
            captured += 1
    if captured != len(monthly_keys):
        logging.error(f"Expecting {len(monthly_keys)} monthly observation fields but only got got {captured}")
        logging.error(f" -> Expected: {', '.join(monthly_keys)}")
        sys.exit(1)
    return col_map


def validate_xlsx(xlsx, yml_dict) -> Tuple[Worksheet, datetime, Dict[str, int]]:
    wb = load_workbook(filename=xlsx)

    ws = wb.active

    col_max = ws.max_column + 1
    # scan first row to find col-spans, add to list
    row = 1
    ranges = ranges_in_row(ws, row, col_max)
    cfg_month_sets = yml_dict["monthly_observation_sets"]
    exp_ranges = cfg_month_sets["spans_expected"]
    if len(ranges) != exp_ranges:
        logging.error(f"Expecting {exp_ranges} date spans in row 1, got {len(ranges)}")
        logging.error(f"Edit config changing 'monthly_observation_sets.spans_expected' if this has changed.")
        sys.exit(1)

    # needs to be applied to each row_object
    monthly_date = datetime.strptime(
        ws.cell(1, ranges[cfg_month_sets["span_used_idx"]][0]).value, cfg_month_sets["date_parse"]
    )

    # core columns stop at first range:
    core_stop = ranges[0][0] - 1
    if core_stop < len(yml_dict["core_fields"]):
        logging.error(f"Insifficient column before first date range to support:")
        logging.error(f" -> {', '.join(yml_dict['core_fields'].keys())}")

    # generate the column mappings for each field
    col_map = core_cols(yml_dict, ws, core_stop)
    col_map = monthly_cols(yml_dict, ws, ranges[cfg_month_sets["span_used_idx"]], col_map)
    return (ws, monthly_date, col_map)
