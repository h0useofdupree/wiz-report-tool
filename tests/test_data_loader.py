from pathlib import Path
from wiz_report_tool.data_loader import load_csv


def test_load_csv():
    fixture = Path(__file__).parent / "fixtures" / "sample.csv"
    with open(fixture, "r", encoding="utf-8") as f:
        df = load_csv(f)
    assert list(df.columns) == ["id", "name", "score"]
    assert len(df) == 3
