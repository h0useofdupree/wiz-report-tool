import pandas as pd
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
