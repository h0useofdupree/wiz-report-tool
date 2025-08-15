import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="WIZ Report Viewer", layout="wide")


def load_csv(file) -> pd.DataFrame:
    """Load CSV from uploaded file into a DataFrame.
    Handles common separators and missing values.
    """
    df = pd.read_csv(file, delimiter=";", encoding="utf-8", low_memory=False)
    return df


def render_df(df: pd.DataFrame):
    """Render DataFrame with link column conversion.
    Columns named containing "url" will be rendered as hyperlinks.
    """
    # Convert URL columns to markdown links
    for col in df.columns:
        if "url" in col.lower():
            df[col] = df[col].apply(
                lambda u: f"[Link]({u})" if pd.notna(u) and str(u).strip() else ""
            )
    st.dataframe(df, use_container_width=True)


def export_excel(df: pd.DataFrame, filename: str = "report.xlsx"):
    """Return BytesIO buffer of Excel file."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output


def main():
    st.title("WIZ Report Viewer")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is None:
        st.info("Please upload a CSV file to proceed.")
        return

    df = load_csv(uploaded_file)

    # Sorting UI
    st.subheader("Sort")
    sort_cols = st.multiselect("Columns", options=list(df.columns))
    if sort_cols:
        orders = []
        for col in sort_cols:
            orders.append(
                st.checkbox(f"Ascending for {col}", value=True, key=f"asc_{col}")
            )
        df = df.sort_values(by=sort_cols, ascending=orders)

    # Filtering UI
    st.subheader("Filter")
    filter_col = st.selectbox(
        "Filter column", options=["None"] + list(df.columns), key="filter_col"
    )
    if filter_col != "None":
        filter_val = st.text_input("Filter value", key="filter_val")
        if filter_val:
            df = df[
                df[filter_col]
                .astype(str)
                .str.contains(filter_val, case=False, na=False)
            ]

    # Render table
    render_df(df)

    # Export to Excel
    st.subheader("Export")
    excel_data = export_excel(df)
    st.download_button(
        label="Download as Excel",
        data=excel_data,
        file_name="report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    main()
