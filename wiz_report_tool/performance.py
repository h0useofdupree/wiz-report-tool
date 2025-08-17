"""Utilities for measuring CSV loading performance."""

from __future__ import annotations

from pathlib import Path
from typing import Dict
from importlib.util import find_spec
import time
import pandas as pd


def benchmark_csv(path: Path, repeats: int = 3) -> Dict[str, float]:
    """Benchmark CSV loading for available pandas engines.

    Parameters
    ----------
    path:
        Path to the CSV file.
    repeats:
        How many times each engine should load the file. The returned value is
        the average duration in seconds.

    Returns
    -------
    dict
        Mapping of engine name to average load duration.
    """
    engines = ["c"]
    if find_spec("pyarrow") is not None:
        engines.append("pyarrow")

    results: Dict[str, float] = {}
    for engine in engines:
        total = 0.0
        for _ in range(repeats):
            start = time.perf_counter()
            kwargs = {"delimiter": ";", "encoding": "utf-8", "engine": engine}
            if engine != "pyarrow":
                kwargs["low_memory"] = False
            pd.read_csv(path, **kwargs)
            total += time.perf_counter() - start
        results[engine] = total / repeats
    return results
