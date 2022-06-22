"""Database related functions."""
import getpass
import logging
import sys
from inspect import cleandoc
from typing import Any

import mysql.connector
from mysql.connector.cursor import MySQLCursor

# import MySQLdb


def insert_stmnt(db: str) -> str:
    """Create insert statement for relevant db/schema.

    Args:
        db: The database/schema name to target.

    Returns:
        Leading whitespace stripped SQL insert.
    """
    stmnt = f"""
    insert into {db}.temp_whzan_monthly_data
    (activity_month,Caseload,Caseload_Size,Days_Since_Last_Reading,BP,Pulse,O2,Temp,NEWS,`NEWS2(0-4)`,`NEWS2(5-6)`,`NEWS2(7+)`,NEWS2,Photos,ECG,Stethoscope,Clients_with_Readings)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    return cleandoc(stmnt)


def count_month_stmnt(db: str) -> str:
    """Create count distinct records for month statement for relevant db/schema.

    Args:
        db: The database/schema name to target.

    Returns:
        Leading whitespace stripped SQL insert.
    """
    stmnt = f"""
    select count(*) as curr_rows
    from (
        select distinct * from
        {db}.temp_whzan_monthly_data
        where activity_month = %(month)s
    ) x
    """
    return cleandoc(stmnt)


def get_month_count(cursor: MySQLCursor, query: str, month: str) -> int:
    """Execute and get the unique count of records for the month.

    Args:
        cursor: Database cursor.
        query: query string.
        month: month, same as insert format.

    Returns:
        Count of unique records for the specified month.
    """
    cursor.execute(query, {"month": month})
    count = cursor.fetchone()[0]
    return count


def upload(config: dict[str, Any], db_rows: list[list[Any]]):
    """Connect to database and insert records.

    Requests password interactively, masked with no indication of keystrokes.

    If insertion of rows results in no new unique rows the changes are aborted.
    Approach is unusual as the target table has no unique constraints due to data issues.

    Args:
        config: Config loaded into dict.
        db_rows: Rows to be loaded.
    """
    host = config["connection"]["host"]
    port = config["connection"]["port"]
    db = config["connection"]["db"]
    user = config["connection"]["user"]

    if "pw" in config["connection"]:
        pwd = config["connection"]["pw"]
        logging.warn("Password exposed in plain text, only for unit-testing.")
    else:
        pwd = getpass.getpass(prompt=">>>>> Please enter password for above DB: ", stream=None)

    logging.info("")
    logging.info("About to connect to:")
    logging.info(f"\t{host}:{port}")
    logging.info(f"\tDB={db}, User={user}")
    logging.info("")

    sql_insert = insert_stmnt(db)
    sql_count = count_month_stmnt(db)

    logging.info("Connecting to DB")
    connection = mysql.connector.connect(user=user, password=pwd, host=host, port=int(port), database=db)
    logging.info("Creating transaction")
    cursor = connection.cursor()

    month = db_rows[0][0]
    count_start = get_month_count(cursor, sql_count, month)

    logging.info("Loading data")
    overlap_count = 0
    for row in db_rows:
        cursor.execute(sql_insert, row)

    count_end = get_month_count(cursor, sql_count, month)

    unique_rows = count_end - count_start

    if unique_rows == 0:
        logging.error("No unique records added, suspect reload of existing data.")
        logging.error("Changes rolled back")
        connection.rollback()
        connection.close()
        sys.exit(1)
    else:
        logging.info(f"Added {len(db_rows)} records for {month}.")
        logging.info("Committing changes")
        connection.commit()
        connection.close()
