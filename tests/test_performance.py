import pandas as pd
from pathlib import Path

from wiz_report_tool.performance import benchmark_csv


def test_benchmark_csv(tmp_path):
    sizes = [100, 1000]
    for n in sizes:
        df = pd.DataFrame({"id": range(n)})
        csv_path = tmp_path / f"sample_{n}.csv"
        df.to_csv(csv_path, sep=";", index=False)
        results = benchmark_csv(csv_path, repeats=1)
        print(f"size={n} -> {results}")
        assert "c" in results
        for t in results.values():
            assert t >= 0


def test_benchmark_csv_sample_files():
    data_dir = Path(__file__).parent / "sample_data"
    for csv_path in sorted(data_dir.glob("sample_*.csv")):
        expected_rows = int(csv_path.stem.split("_")[-1])
        results = benchmark_csv(csv_path, repeats=1)
        print(f"file={csv_path.name} -> {results}")
        df = pd.read_csv(csv_path, sep=";")
        assert len(df) == expected_rows
        assert "c" in results
        for t in results.values():
            assert t >= 0
