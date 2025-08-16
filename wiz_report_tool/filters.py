import pandas as pd
import streamlit as st


def apply_filters(df: pd.DataFrame, filter_rows, logic: str, numeric_cols, date_cols):
    """Apply filter rows to DataFrame and return filtered DataFrame."""
    mask = None
    for column, condition, value1, value2 in filter_rows:
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

    return df


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Interactive sorting and filtering controls for a DataFrame."""
    numeric_cols: list[str] = []
    date_cols: list[str] = []
    for col in df.columns:
        series = df[col]
        non_empty = series.astype(str).str.strip() != ""
        num_series = pd.to_numeric(series, errors="coerce")
        if non_empty.any() and num_series[non_empty].notna().all():
            df[col] = num_series
            numeric_cols.append(col)
            continue

        date_series = pd.to_datetime(series, errors="coerce")
        if non_empty.any() and date_series[non_empty].notna().all():
            if pd.api.types.is_datetime64tz_dtype(date_series):
                date_series = date_series.dt.tz_localize(None)
            df[col] = date_series
            date_cols.append(col)

    st.subheader("Sort")
    sort_cols = st.multiselect("Columns", options=list(df.columns))
    if sort_cols:
        orders = []
        for col in sort_cols:
            orders.append(
                st.checkbox(f"Ascending for {col}", value=True, key=f"asc_{col}")
            )
        df = df.sort_values(by=sort_cols, ascending=orders)

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

    df = apply_filters(df, filter_rows, logic, numeric_cols, date_cols)
    return df
