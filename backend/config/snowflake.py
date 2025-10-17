import snowflake.connector
from typing import Generator
from .settings import settings


def get_snowflake_connection() -> Generator[snowflake.connector.SnowflakeConnection, None, None]:
    account = (settings.snowflake_account or "").strip()
    user = (settings.snowflake_user or "").strip()
    password = (settings.snowflake_password or "").strip()
    warehouse = (settings.snowflake_warehouse or "").strip()
    database = (settings.snowflake_database or "").strip()
    schema = (settings.snowflake_schema or "").strip()

    try:
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse or None,
            database=database or None,
            schema=schema or None,
        )

        # Explicitly set context in case connector ignored blanks/whitespace
        cur = conn.cursor()
        try:
            if warehouse:
                cur.execute(f"USE WAREHOUSE {warehouse}")
            if database:
                cur.execute(f"USE DATABASE {database}")
            if schema:
                cur.execute(f"USE SCHEMA {schema}")
        finally:
            cur.close()

        yield conn
    except Exception as e:
        print(f"Snowflake connection error: {e}")
        print(f"Account: {account}, User: {user}, Warehouse: {warehouse}, Database: {database}, Schema: {schema}")
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass


