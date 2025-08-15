# AGENTS

## Project Overview

This repository contains **wiz-report-tool**, a small Streamlit application for
browsing CSV reports from WiZ/CyCognito. The app lets users upload a report,
sort and filter the data, and export the view to Excel.

### Layout

- `app.py` – Streamlit application entry point.
- `requirements.txt` – Python dependencies for the app.
- `flake.nix` / `flake.lock` – Nix flake defining the development environment.
- `.envrc` – contains `use flake` so `direnv` automatically loads the dev shell.
- `Daily_Issue_Report_filtered_by_WIZOwnership_*.csv` – sample report for local
  testing.

## Working with the Project

- Check that the code compiles:
  ```bash
  python -m py_compile app.py
  ```
- Run the Streamlit app:
  ```bash
  streamlit run app.py
  ```
- The `.venv` directory and other build artifacts are ignored by git; keep
  commits focused on source files.

**Happy coding!**
