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
    # Drop tz info for excel export
    df = df.copy()
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)

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

    # Identify numericc and datetime columns
    numeric_cols: list[str] = []
    date_cols: list[str] = []
    for col in df.columns:
        series = df[col]
        # HACK: Only treat as numeric if all non-empty values are numeric
        # (should prevent mixed cols like subscription-id)
        non_empty = series.astype(str).str.strip() != ""
        num_series = pd.to_numeric(series, errors="coerce")
        if non_empty.any() and num_series[non_empty].notna().all():
            df[col] = num_series
            numeric_cols.append(col)
            continue

        # HACK: Only convert to datetimes if all populated rows parse
        date_series = pd.to_datetime(series, errors="coerce")
        if non_empty.any() and date_series[non_empty].notna().all():
            if pd.api.types.is_datetime64tz_dtype(date_series):
                date_series = date_series.dt.tz_localize(None)
            df[col] = date_series
            date_cols.append(col)

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
    if "filter_count" not in st.session_state:
        st.session_state.filter_count = 1
    if st.button("Add filter"):
        st.session_state.filter_count += 1
    logic = st.radio("Combine conditions with", ["AND", "OR"], horizontal=True)

    filter_rows = []
    for i in range(st.session_state.filter_count):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            column = st.selectbox(
                f"Column {i + 1}", options=list(df.columns), key=f"f_col_{i}"
            )
        with col2:
            options = ["equals", "contains"]
            if column in numeric_cols or column in date_cols:
                options.extend(["gt", "lt", "range"])
            condition = st.selectbox(
                f"Condition {i + 1}", options=options, key=f"f_cond_{i}"
            )
        with col3:
            if condition == "range":
                value1 = st.text_input("From", key=f"f_val1_{i}")
            else:
                value1 = st.text_input("Value", key=f"f_val_{i}")
        with col4:
            value2 = (
                st.text_input("To", key=f"f_val2_{i}") if condition == "range" else None
            )
        filter_rows.append((column, condition, value1, value2))

    mask = None
    for column, condition, value1, value2 in filter_rows:
        # Skip invalid rows
        if condition == "range":
            if not value1 or not value2:
                continue
        else:
            if not value1:
                continue

        series = df[column]
        if column in numeric_cols:
            v1 = pd.to_numeric(value1, errors="coerce")
            if condition == "equals":
                row_mask = series == v1
            elif condition == "gt":
                row_mask = series > v1
            elif condition == "lt":
                row_mask = series < v1
            elif condition == "range":
                v2 = pd.to_numeric(value2, errors="coerce")
                row_mask = series.between(v1, v2)
            else:
                row_mask = series.astype(str).str.contains(value1, case=False, na=False)
        elif column in date_cols:
            v1 = pd.to_datetime(value1, errors="coerce")
            if condition == "equals":
                row_mask = series == v1
            elif condition == "gt":
                row_mask = series > v1
            elif condition == "lt":
                row_mask = series < v1
            elif condition == "range":
                v2 = pd.to_datetime(value2, errors="coerce")
                row_mask = series.between(v1, v2)
            else:
                row_mask = series.astype(str).str.contains(value1, case=False, na=False)
        else:
            if condition == "equals":
                row_mask = series.astype(str).str.lower() == value1.lower()
            else:
                row_mask = series.astype(str).str.contains(value1, case=False, na=False)

        if mask is None:
            mask = row_mask
        else:
            mask = mask & row_mask if logic == "AND" else mask | row_mask

    if mask is not None:
        df = df[mask]

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
