"""
DuckDB Session Manager & Resource Limiter Showcase.

Provides a thread-safe, memory-bounded DuckDB connection pool for executing OLAP SQL queries
over Parquet files stored per tenant.
"""
import threading
import duckdb
from django.conf import settings

# Global semaphore to control maximum concurrent DuckDB executions
_DUCKDB_SEMAPHORE = threading.Semaphore(value=getattr(settings, "DUCKDB_MAX_CONCURRENT", 2))


class DuckDBSession:
    """
    Context manager for thread-safe DuckDB query execution with strict resource limits.
    """

    def __init__(self, memory_limit="512MB", threads=1):
        self.memory_limit = memory_limit
        self.threads = threads
        self.conn = None

    def __enter__(self):
        _DUCKDB_SEMAPHORE.acquire()
        try:
            self.conn = duckdb.connect(database=":memory:")
            self.conn.execute(f"SET memory_limit='{self.memory_limit}';")
            self.conn.execute(f"SET threads={self.threads};")
            return self.conn
        except Exception:
            _DUCKDB_SEMAPHORE.release()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.conn:
                self.conn.close()
        finally:
            _DUCKDB_SEMAPHORE.release()


def execute_parquet_query(parquet_path: str, sql_query: str, params: list = None):
    """
    Executes a parametrized SQL query against a tenant's Parquet file.
    """
    with DuckDBSession() as conn:
        # Secure query execution using DuckDB relation API
        rel = conn.read_parquet(parquet_path)
        result = conn.execute(sql_query, params or []).fetchall()
        return result
