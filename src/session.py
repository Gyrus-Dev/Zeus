import os
import logging
import pyodbc
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)
_debug = os.environ.get("ZEUSAI_DEBUG")
logger.setLevel(logging.DEBUG if _debug else logging.WARNING)

# Module-level connection cache
_connection_cache: Dict[tuple, Any] = {}


class Session:
    def __init__(self):
        self._host = None
        self._port = 1433
        self._user = None
        self._password = None
        self._database = None
        self._driver = os.environ.get("SQLSERVER_DRIVER", "{ODBC Driver 18 for SQL Server}")
        self._trust_cert = os.environ.get("SQLSERVER_TRUST_SERVER_CERTIFICATE", "yes")
        self._connection = None

    def set_host(self, value): self._host = value
    def set_port(self, value): self._port = int(value) if value else 1433
    def set_user(self, value): self._user = value
    def set_password(self, value): self._password = value
    def set_database(self, value): self._database = value

    def get_connection(self):
        if not self._host or not self._user:
            raise ValueError("SQL Server credentials missing — host and user are required.")
        if not self._password:
            raise ValueError("SQL Server password is required.")

        cache_key = (self._host, self._port, self._user, self._database)
        if cache_key in _connection_cache:
            conn = _connection_cache[cache_key]
            try:
                # Probe liveness with a lightweight operation
                conn.getinfo(pyodbc.SQL_DATABASE_NAME)
                return conn
            except Exception:
                pass
            del _connection_cache[cache_key]

        connection_string = (
            f"DRIVER={self._driver};"
            f"SERVER={self._host},{self._port};"
            f"DATABASE={self._database or 'master'};"
            f"UID={self._user};"
            f"PWD={self._password};"
            f"TrustServerCertificate={self._trust_cert};"
        )
        conn = pyodbc.connect(connection_string, autocommit=True)
        _connection_cache[cache_key] = conn
        self._connection = conn
        logger.debug("SQL Server connection established for user=%s host=%s", self._user, self._host)
        return conn

    def execute(self, query: str) -> list:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return []
        finally:
            cursor.close()
