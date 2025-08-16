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
    render_df(df)

    render_export(df)


if __name__ == "__main__":
    main()
