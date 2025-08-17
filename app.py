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

    # Sidebar configuration for conditional formatting
    if "highlight_rules" not in st.session_state:
        st.session_state.highlight_rules = []

    st.sidebar.header("Highlight Rules")
    with st.sidebar.expander("Add rule"):
        rule_col = st.selectbox("Column", options=list(df.columns), key="hr_col")
        rule_op = st.selectbox(
            "Condition", options=[">", "<", "==", "contains"], key="hr_op"
        )
        rule_val = st.text_input("Value", key="hr_val")
        rule_color = st.color_picker("Color", "#ffff00", key="hr_color")
        if st.button("Add", key="hr_add"):
            typed_val = rule_val
            if rule_op in [">", "<", "=="] and pd.api.types.is_numeric_dtype(
                df[rule_col]
            ):
                try:
                    typed_val = float(rule_val)
                except ValueError:
                    st.sidebar.warning("Enter a numeric value for this column")
                    typed_val = None
            if typed_val is not None:
                st.session_state.highlight_rules.append(
                    {
                        "column": rule_col,
                        "op": rule_op,
                        "value": typed_val,
                        "color": rule_color,
                    }
                )
    if st.sidebar.button("Clear rules"):
        st.session_state.highlight_rules = []

    for r in st.session_state.highlight_rules:
        st.sidebar.write(
            f"{r['column']} {r['op']} {r['value']} -> {r.get('color', 'yellow')}"
        )

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

    render_df(df, highlight_rules=st.session_state.highlight_rules)
    render_export(df)


if __name__ == "__main__":
    main()
