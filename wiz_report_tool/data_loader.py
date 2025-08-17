import pandas as pd
from importlib.util import find_spec


def load_csv(file) -> pd.DataFrame:
    """Load CSV from uploaded file into a DataFrame.
    Handles common separators and missing values.
    Uses the ``pyarrow`` engine when available for faster parsing
    """
    kwargs = {"delimiter": ";", "encoding": "utf-8"}
    if find_spec("pyarrow") is not None:
        kwargs["engine"] = "pyarrow"
    else:
        kwargs["low_memory"] = False
    df = pd.read_csv(file, **kwargs)
    return df
