import pandas as pd


def load_csv(file) -> pd.DataFrame:
    """Load CSV from uploaded file into a DataFrame.
    Handles common separators and missing values.
    """
    df = pd.read_csv(file, delimiter=";", encoding="utf-8", low_memory=False)
    return df
