"""Data loader module for the Smart ICU Equipment Predictive Monitoring platform.

Handles reading raw datasets from CSV files into Pandas DataFrames, performing basic
file-level existence checks and logging performance metrics.
"""

import os
import pandas as pd
from typing import Union
from pathlib import Path
from src.config import RAW_DATA_PATH
from src.utils import get_logger

logger = get_logger("src.data_loader")

def load_raw_telemetry(filepath: Union[str, Path] = RAW_DATA_PATH) -> pd.DataFrame:
    """Reads raw telemetry data from a CSV file.

    Args:
        filepath: File path to the raw CSV file. Defaults to RAW_DATA_PATH.

    Returns:
        pd.DataFrame: Raw telemetry dataset.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    logger.info(f"Initiating raw data load from path: {filepath}")
    
    if not os.path.exists(filepath):
        error_msg = f"Raw telemetry dataset file not found at: {filepath}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
        
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Successfully loaded raw telemetry dataset. Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Failed to read CSV telemetry file: {e}")
        raise e
