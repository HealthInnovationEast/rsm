# Remote site monitoring <!-- omit in toc -->

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

| Branch  |                   GitHub Action Status                    |
| :-----: | :-------------------------------------------------------: |
|  main   |    ![pre-commit][pre-commit-main] ![build][build-main]    |
| develop | ![pre-commit][pre-commit-develop] ![build][build-develop] |

**This package is highly unlikely to be of use outside of Eastern AHSN.**

- [Overview](#overview)
- [Commands](#commands)
- [The use-case](#the-use-case)
  - [Approach](#approach)
    - [Validation](#validation)
    - [CSV mode](#csv-mode)
    - [Direct load to mysql](#direct-load-to-mysql)
- [Configuration](#configuration)
- [Development](#development)
  - [Initial setup](#initial-setup)
  - [Testing](#testing)
  - [Code documentation](#code-documentation)

## Overview

This tool provides the following functionality:

1. Check validity of `xlsx` data file for remote monitoring datasets.
1. Clean and convert to appropriate data formats for either:
   - manual sql load to warehouse
   - transactional load to warehouse

## Commands

This project uses sub commands, to list the available commands execute:

```console
rsm --help
```

Additional help is available for each subcommand via:

```console
rsm [subcommand] --help
```

The most useful commands are:

- `rsm template-config` - Dump example yaml config file to stdout.
  - The only needs modification when using `rsm to-db`
- `rsm to-csv` - Generate the processed CSV file.
- `rsm to-db` - Directly load into database, generates CSV for records.

## The use-case

Input data arrives in the form of 2 `xlsx` spreadsheets, there are 2 problem with these:

1. Not designed with automatic ingestion in mind
1. No change control, columns "appear" between months

### Approach

Historically the process has been manual, involving removal of columns, format updates and transposing fields from
headings to row level items.

The main issue is that the report includes partial and historical months, however the heading spans are useful.

- The monthly data we want is under the second cell with a "span" applied in row 1
- The date to be applied to all records can be taken from this cell
- Scanning headings under the 2nd span:
  - retain only those listed in `parser.cfg.yaml`
  - warn on all items not excpected for user information
  - error if heading not found
- Load all data rows into dict based on retained field and date from 2nd span
  - Where data format not defined in `parser.cfg.yaml` apply integer conversion

This provides sufficient loaded data for a validation.

#### Validation

Performs full parse of data, giving 0 (success) or non-zero exitcode as appropriate.  Validations applied:

- Expected number of merged cells in row 1 (month ranges)
  - defined in config as `monthly_observation_sets.spans_expected`
- Sufficient columns before first merged cell in row 1 to support core columns
  - Compared against number of `core_fields` in config
- Presence of core columns between col A and the first merged cell range
  - All headings under `core_fields` are found
- Within the selected month range (config `monthly_observation_sets.span_used_idx`) all expected headings found
  - Listed under `monthly_observations`

#### CSV mode

Generate csv vesion of file columns ordered as described in `parser.cfg.yaml`

Date to be formatted as `{month.title()}-{year.2digit}`, do as part of writer.

The generated CSV file can be used with the manual load process.

#### Direct load to mysql

Date format is different, to remove need for additional updates after load.

## Configuration

The validity check will be controlled by a `yaml` configuration file detailing expected content of specific cells.

All cell contents will have line breaks removed before matching.

Please run `rsm template-config` to get the full config file.

## Development

If on Windows we're assuming use of the bash command line provided by git install.

### Initial setup

Adds the virtual env and installs package in dev mode:

```bash
cd ## your-checkout ##
python -m venv .venv
. .venv/Scripts/activate
pip install --editable .[mysql]
# if you want don't want to use direct mysql loading
# install without the mysql module (mainly for if there are issues)
pip install --editable .
```

### Testing

Basic input/output tests are in place.  To execute with coverage reports:

```bash
# !!! Assumes venv is active !!!
# first time:
pip install --editable .[tests]
pytest . -x --no-cov-on-fail --cov=rsm --cov-report term --cov-report html --junitxml=junit.xml
```

### Code documentation

Browsable code documentation can be viewed locally via:

```bash
# !!! Assumes venv is active !!!
# first time
pip install --editable .[docs]
mkdocs serve
```

The documentation is automatically rendered from the doc strings in code.

If a new file is added to `src/` please add a corresponding `docs/rsm/*.md`.

<!-- refs -->

[build-develop]: https://github.com/cynapse-ccri/rsm/actions/workflows/build.yaml/badge.svg?branch=develop
[build-main]: https://github.com/cynapse-ccri/rsm/actions/workflows/build.yaml/badge.svg?branch=main
[pre-commit-develop]: https://github.com/cynapse-ccri/rsm/actions/workflows/pre-commit.yaml/badge.svg?branch=develop
[pre-commit-main]: https://github.com/cynapse-ccri/rsm/actions/workflows/pre-commit.yaml/badge.svg?branch=main
