# Repository Guidelines

## 1. Project Structure & Module Organization
```
wiz-report-tool/
│   README.md
│   AGENTS.md
│   app.py            # Main Streamlit entry point
│   requirements.txt  # Runtime dependencies
└───────
```
* `app.py` implements the data‑loading, UI, and export logic.  All
  interactive behaviour lives in this single script for the current prototype.
* Tests are not yet included – future extensions should follow the same layout as
  typical Python projects (e.g., a `tests/` folder with `test_*.py`).

## 2. Build, Test, and Development Commands
*`pip install -r requirements.txt`* – Installs `streamlit`, `pandas`, and `openpyxl`.
*`streamlit run app.py`* –  Starts the viewer locally.
*`streamlit build app.py`* –  (Optional) Builds a static version for sharing.

## 3. Coding Style & Naming Conventions
* **Indentation** – 4‑space tabs (no Tab characters).
* **Python** – Follow `black` format rules; run `black app.py` before any commit.
* **Variable names** – Snake_case for variables, UPPERCASE for constants.
* **Function names** – `lowercase_with_underscores` that describe the action.
  Example: `load_csv`, `render_df`.

## 4. Testing Guidelines
* Testing is currently empty, but we plan to use **pytest** once the first
  integration tests are written.
* Tests should live in `tests/` and be named `test_*.py`.
* Run tests with `pytest` from the project root:
```
pytest --maxfail=1 --disable-warnings
```
Coverage is not yet enforced but will be added in future iterations.

## 5. Commit & Pull Request Guidelines
* **Commit messages** – 3‑word imperative subject, e.g. `Add CSV loader`.
* **Pull requests** – Include a clear description, link to any related issue (`#<number>`), and,
  if applicable, a screenshot of new UI behaviour.
* **Review** – Peer review required; approvals by at least one maintainer.

Happy coding! Feel free to open an issue if a section needs clarification.
