import io
import pandas as pd
import streamlit as st


def render_df(df: pd.DataFrame, highlight_rules: list[dict] | None = None):
    """Render DataFrame with optional conditional formatting.

    Columns with names containing ``"url"`` will be rendered as hyperlinks.
    ``highlight_rules`` is a list of dictionaries describing formatting
    operations.  Each rule must contain ``column``, ``op`` (one of ``>
    < == contains``), ``value`` and an optional ``color``.  When provided,
    ``pandas.Styler`` is used to highlight cells meeting the condition.
    """

    df = df.copy()

    for col in df.columns:
        if "url" in col.lower():
            df[col] = df[col].apply(
                lambda u: f"[Link]({u})" if pd.notna(u) and str(u).strip() else ""
            )

    styler = df.style

    def _apply_rule(s: pd.Series, op: str, value, color: str):
        try:
            if op == ">":
                mask = s > value
            elif op == "<":
                mask = s < value
            elif op == "==":
                mask = s == value
            elif op == "contains":
                mask = s.astype(str).str.contains(str(value), na=False)
            else:
                mask = pd.Series([False] * len(s))
        except Exception:
            mask = pd.Series([False] * len(s))
        return [f"background-color: {color}" if m else "" for m in mask]

    if highlight_rules:
        for rule in highlight_rules:
            color = rule.get("color", "yellow")
            styler = styler.apply(
                lambda s, r=rule, c=color: _apply_rule(
                    s, r.get("op", "=="), r.get("value"), c
                ),
                subset=[rule.get("column")],
            )
        st.dataframe(styler, use_container_width=True)
    else:
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
