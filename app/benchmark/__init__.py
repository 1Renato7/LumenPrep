"""Reproducible, server-mediated benchmark and Parquet materialization."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .parquet import BenchmarkReport

__all__ = ["BenchmarkReport", "materialize_canonical_events", "run_historical_parquet_benchmark"]


def __getattr__(name: str):
    if name in __all__:
        from . import parquet

        return getattr(parquet, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
