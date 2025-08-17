import pandas as pd
import streamlit as st
from wiz_report_tool.data_loader import load_csv
from wiz_report_tool.filters import filter_dataframe
from wiz_report_tool.ui import render_df, render_export

st.set_page_config(page_title="WIZ Report Viewer", layout="wide")


def main():
    st.title("WIZ Report Viewer")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is None:
        st.info("Please upload a CSV file to proceed.")
        return

    df = load_csv(uploaded_file)

    df = filter_dataframe(df)

    # NOTE: Basic metrics visualisation
    st.subheader("Summary")
    summary_col = st.selectbox("Column to summarize", options=list(df.columns))
    counts = df[summary_col].value_counts()

    col1, col2 = st.columns(2)
    col1.metric("Total rows", len(df))
    col2.metric("Unique values", len(counts))

    st.write(counts)
    if pd.api.types.is_numeric_dtype(df[summary_col]):
        st.line_chart(counts)
    else:
        st.bar_chart(counts)

    render_df(df)
    render_export(df)


if __name__ == "__main__":
    main()
