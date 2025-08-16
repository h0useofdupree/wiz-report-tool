import io
import pandas as pd
import streamlit as st


def render_df(df: pd.DataFrame):
    """Render DataFrame with link column conversion.
    Columns named containing 'url' will be rendered as hyperlinks."""
    for col in df.columns:
        if "url" in col.lower():
            df[col] = df[col].apply(
                lambda u: f"[Link]({u})" if pd.notna(u) and str(u).strip() else ""
            )
    st.dataframe(df, use_container_width=True)


def export_excel(df: pd.DataFrame, filename: str = "report.xlsx"):
    """Return BytesIO buffer of Excel file."""
    df = df.copy()
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output


def render_export(df: pd.DataFrame, filename: str = "report.xlsx"):
    """Render export UI components for DataFrame."""
    st.subheader("Export")
    excel_data = export_excel(df, filename=filename)
    st.download_button(
        label="Download as Excel",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
