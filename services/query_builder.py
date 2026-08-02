"""
Safe SQL Query Builder Showcase.

Constructs sanitized SQL aggregation queries for chart visualization
without exposing raw SQL injection vulnerabilities to the frontend.
"""
from typing import Dict, Any, List


class SafeQueryBuilder:
    """
    Parametrized query builder for chart aggregations (SUM, AVG, COUNT, MIN, MAX).
    """

    ALLOWED_AGGREGATIONS = {"SUM", "AVG", "COUNT", "MIN", "MAX", "COUNT_DISTINCT"}

    @classmethod
    def build_chart_query(
        cls,
        parquet_path: str,
        dimension_col: str,
        metric_col: str,
        aggregation: str,
        limit: int = 100
    ) -> tuple[str, List[Any]]:
        """
        Builds a safe, parametrized SQL string and parameter tuple.
        """
        agg = aggregation.upper()
        if agg not in cls.ALLOWED_AGGREGATIONS:
            raise ValueError(f"Invalid aggregation function: {aggregation}")

        # Sanitize column names using quoted identifier escaped pattern
        clean_dim = dimension_col.replace('"', '""')
        clean_metric = metric_col.replace('"', '""')

        if agg == "COUNT_DISTINCT":
            agg_expr = f"COUNT(DISTINCT \"{clean_metric}\")"
        else:
            agg_expr = f"{agg}(\"{clean_metric}\")"

        query = f"""
            SELECT
                "{clean_dim}" AS dimension,
                {agg_expr} AS metric
            FROM read_parquet(?)
            GROUP BY "{clean_dim}"
            ORDER BY metric DESC
            LIMIT ?
        """

        params = [parquet_path, limit]
        return query, params
