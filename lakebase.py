"""
Lakebase connection helper.
"""

import base64
import os

import psycopg2

from contextlib import contextmanager
from databricks.sdk import WorkspaceClient
from psycopg2.extras import RealDictCursor


_workspace = WorkspaceClient()


SCOPE = os.getenv(
    "LAKEBASE_SECRET_SCOPE",
    "database"
)

KEY = os.getenv(
    "LAKEBASE_SECRET_KEY",
    "lakebase-url"
)


def get_lakebase_url():

    secret = _workspace.secrets.get_secret(
        scope=SCOPE,
        key=KEY
    )

    return base64.b64decode(
        secret.value
    ).decode("utf-8")


@contextmanager
def get_connection():

    conn = psycopg2.connect(
        get_lakebase_url(),
        cursor_factory=RealDictCursor
    )

    try:
        yield conn

    finally:
        conn.close()

def run_query(query, params=None):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT current_database();")
    print("DATABASE:", cursor.fetchone())

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
    """)
    print("TABLES:", cursor.fetchall())

    cursor.execute(query, params)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results
    
def run_query(sql, params=None):

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                sql,
                params
            )

            return cursor.fetchall()



def run_write(sql, params=None):

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                sql,
                params
            )

            conn.commit()

            return cursor.rowcount