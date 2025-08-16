from pathlib import Path
import openpyxl
from wiz_report_tool.data_loader import load_csv
from wiz_report_tool.ui import export_excel


def load_fixture_df():
    fixture = Path(__file__).parent / "fixtures" / "sample.csv"
    with open(fixture, "r", encoding="utf-8") as f:
        return load_csv(f)


def test_export_excel(tmp_path):
    df = load_fixture_df()
    buffer = export_excel(df)
    assert buffer.getbuffer().nbytes > 0
    out_file = tmp_path / "out.xlsx"
    out_file.write_bytes(buffer.getvalue())
    wb = openpyxl.load_workbook(out_file)
    assert wb.active.max_row == len(df) + 1
