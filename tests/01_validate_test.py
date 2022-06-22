import filecmp
import os
import tempfile

import pytest
import rsm.main as rsm_main

DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data",
)

EXPECTED = os.path.join(DATA_DIR, "Expected.csv")


@pytest.mark.parametrize(
    "input",
    [
        (os.path.join(DATA_DIR, "Input_71cols.xlsx")),
        (os.path.join(DATA_DIR, "Input_74cols.xlsx")),
    ],
)
def test_01_valid_inputs(input):
    rsm_main.validate(input, None, "INFO")
    assert True


@pytest.mark.parametrize(
    "input, expected",
    [
        (os.path.join(DATA_DIR, "Input_71cols.xlsx"), EXPECTED),
        (os.path.join(DATA_DIR, "Input_74cols.xlsx"), EXPECTED),
    ],
)
def test_02_result(input, expected):
    with tempfile.TemporaryDirectory() as tdir:
        outcsv = os.path.join(tdir, "result.csv")
        rsm_main.convert(input, None, outcsv, "INFO")
        assert filecmp.cmp(expected, outcsv), f"Result from {input} does not match expected output {expected}"
