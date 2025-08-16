from pathlib import Path
from wiz_report_tool.data_loader import load_csv
from wiz_report_tool.filters import apply_filters


def load_fixture_df():
    fixture = Path(__file__).parent / "fixtures" / "sample.csv"
    with open(fixture, "r", encoding="utf-8") as f:
        return load_csv(f)


def test_apply_filters_numeric_gt():
    df = load_fixture_df()
    filter_rows = [("score", "gt", "15", None)]
    result = apply_filters(
        df, filter_rows, logic="AND", numeric_cols=["score"], date_cols=[]
    )
    assert result["id"].tolist() == [2, 3]
