# wiz-report-tool

WiZ/CyCognito Report Tool für PVO

## Requirements

The dependencies are documented in `requirements.txt`. Install them using `pip`
before running the app. If nix is used, the devShell will automatically trigger
once in the directory and download all the dependencies.

```bash
pip install -r requirements.txt
```

## Project Structure

The application is split into small modules under the `wiz_report_tool` package:

- `data_loader.py` – CSV loading helpers.
- `filters.py` – sorting and filtering logic.
- `ui.py` – dataframe rendering and export utilities.
- `app.py` – Streamlit entry point wiring the modules together.

## Running the App

The tool is built with Streamlit. Run it locally with:

```bash
streamlit run app.py
```

## Tests

Basic tests cover CSV loading, filtering and export helpers. Run them with:

```bash
pytest
```
