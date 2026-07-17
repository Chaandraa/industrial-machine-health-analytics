"""Data preprocessing, validation, and clinical reframing module.

Responsible for executing the Data Quality Report rules, mapping industrial column
headers to healthcare terms, converting temperature metrics, and generating synthetic
timestamps for time-series demonstrating analytics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from src.config import (
    COLUMN_MAPPING,
    EQUIPMENT_TYPE_MAPPING,
    TEMP_AMBIENT_MIN_K, TEMP_AMBIENT_MAX_K,
    TEMP_INTERNAL_MIN_K, TEMP_INTERNAL_MAX_K,
    FAN_SPEED_MIN_RPM, FAN_SPEED_MAX_RPM,
    MOTOR_LOAD_MIN_NM, MOTOR_LOAD_MAX_NM,
    OPERATING_HOURS_MIN, OPERATING_HOURS_MAX
)
from src.utils import get_logger

logger = get_logger("src.preprocessing")

def run_data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """Generates a structured Data Quality Report dictionary.

    Checks for missing values, duplicates, data types, category checks, range
    violations, and logical data consistency.

    Args:
        df: Input DataFrame (raw or mapped) to audit.

    Returns:
        Dict[str, Any]: Audit results and completeness metrics.
    """
    logger.info("Starting Data Quality Report generation...")
    report: Dict[str, Any] = {}
    
    # 1. Shape and Row Counts
    total_records = len(df)
    report["total_records"] = total_records
    
    # 2. Missing Value Analysis
    missing_counts = df.isnull().sum().to_dict()
    report["missing_values"] = {
        col: {"count": int(count), "percentage": float((count / total_records) * 100)}
        for col, count in missing_counts.items()
    }
    
    # 3. Duplicate Detection
    duplicate_rows = int(df.duplicated().sum())
    # Duplicate Product IDs
    dup_product_ids = 0
    if "Product ID" in df.columns:
        dup_product_ids = int(df.duplicated(subset=["Product ID"]).sum())
    elif "Product_ID" in df.columns:
        dup_product_ids = int(df.duplicated(subset=["Product_ID"]).sum())
        
    report["duplicates"] = {
        "duplicate_rows_count": duplicate_rows,
        "duplicate_product_ids_count": dup_product_ids
    }
    
    # 4. Data Type Validation
    report["data_types"] = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    # 5. Category Validation
    report["invalid_categories"] = {}
    
    # Check Type/Equipment Code categories
    type_col = "Type" if "Type" in df.columns else ("Equipment_Type_Code" if "Equipment_Type_Code" in df.columns else None)
    if type_col:
        valid_types = {"L", "M", "H"}
        invalid_types = df[~df[type_col].isin(valid_types)][type_col].unique().tolist()
        report["invalid_categories"][type_col] = {
            "invalid_found": len(invalid_types) > 0,
            "values": invalid_types
        }
        
    # Check Machine/Device Failure category (must be 0 or 1)
    fail_col = "Machine failure" if "Machine failure" in df.columns else ("Device_Failure" if "Device_Failure" in df.columns else None)
    if fail_col:
        valid_failures = {0, 1}
        invalid_failures = df[~df[fail_col].isin(valid_failures)][fail_col].unique().tolist()
        report["invalid_categories"][fail_col] = {
            "invalid_found": len(invalid_failures) > 0,
            "values": invalid_failures
        }

    # 6. Range Validation (Kelvin units assumed if checking raw data, Celsius if processed)
    report["range_violations"] = {}
    
    # Define mapping to audit ranges
    # We audit in Kelvin for raw columns
    range_checks = [
        ("Air temperature [K]", TEMP_AMBIENT_MIN_K, TEMP_AMBIENT_MAX_K),
        ("Process temperature [K]", TEMP_INTERNAL_MIN_K, TEMP_INTERNAL_MAX_K),
        ("Rotational speed [rpm]", FAN_SPEED_MIN_RPM, FAN_SPEED_MAX_RPM),
        ("Torque [Nm]", MOTOR_LOAD_MIN_NM, MOTOR_LOAD_MAX_NM),
        ("Tool wear [min]", OPERATING_HOURS_MIN, OPERATING_HOURS_MAX)
    ]
    
    for col, min_val, max_val in range_checks:
        if col in df.columns:
            violations_under = int((df[col] < min_val).sum())
            violations_over = int((df[col] > max_val).sum())
            report["range_violations"][col] = {
                "under_range_count": violations_under,
                "over_range_count": violations_over,
                "min_checked": min_val,
                "max_checked": max_val
            }

    # 7. Data Completeness Metrics
    total_nulls = sum(c["count"] for c in report["missing_values"].values())
    report["completeness_percentage"] = float((1 - (total_nulls / (total_records * len(df.columns)))) * 100)
    
    # 8. Data Consistency Checks
    # Original AI4I dataset contains logic where 'Machine failure' is 1, but no failure mode flag is set.
    # We check: If Machine failure == 1, is at least one of (TWF, HDF, PWF, OSF, RNF) set to 1?
    # And: If any of (TWF, HDF, PWF, OSF, RNF) is 1, is Machine failure set to 1?
    report["consistency_checks"] = {
        "failures_without_flags_count": 0,
        "flags_without_failure_count": 0,
        "flag_definitions_consistent": True
    }
    
    failure_modes = ["TWF", "HDF", "PWF", "OSF", "RNF"]
    # Check if renamed failure modes exist
    renamed_failure_modes = ["Failure_Component_Wear", "Failure_Overheating", "Failure_Power_Supply", "Failure_Overload", "Failure_Random_Hardware"]
    
    has_orig_fail_modes = all(m in df.columns for m in failure_modes) and (fail_col in df.columns)
    has_renamed_fail_modes = all(m in df.columns for m in renamed_failure_modes) and (fail_col in df.columns)
    
    if has_orig_fail_modes or has_renamed_fail_modes:
        target_modes = failure_modes if has_orig_fail_modes else renamed_failure_modes
        target_fail_col = "Machine failure" if has_orig_fail_modes else "Device_Failure"
        
        sum_flags = df[target_modes].sum(axis=1)
        
        # Scenario A: Device failed, but no specific mode was flagged
        failures_no_flags = int(((df[target_fail_col] == 1) & (sum_flags == 0)).sum())
        # Scenario B: Specific mode was flagged, but device failure not set (e.g. Random Failure does not always trigger Machine Failure in original data)
        flags_no_failure = int(((df[target_fail_col] == 0) & (sum_flags > 0)).sum())
        
        report["consistency_checks"] = {
            "failures_without_flags_count": failures_no_flags,
            "flags_without_failure_count": flags_no_failure,
            "flag_definitions_consistent": failures_no_flags == 0 and flags_no_failure == 0
        }
        
    logger.info("Data Quality Report compiled successfully.")
    return report

def rename_and_map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renames industrial columns and maps equipment codes to clinical titles.

    Args:
        df: Input raw DataFrame.

    Returns:
        pd.DataFrame: Reframed DataFrame.
    """
    logger.info("Renaming industrial telemetry fields to clinical terms...")
    # Perform column renaming
    renamed_df = df.rename(columns=COLUMN_MAPPING)
    
    # Map 'Equipment_Type_Code' (L, M, H) to descriptive strings
    logger.info("Mapping Equipment Type codes to Ventilators, CT Scanners, and MRI Machines...")
    renamed_df["Equipment_Category"] = renamed_df["Equipment_Type_Code"].map(EQUIPMENT_TYPE_MAPPING)
    
    return renamed_df

def convert_units_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Converts temperatures from Kelvin to Celsius and removes irrelevant columns.

    Args:
        df: Mapped DataFrame.

    Returns:
        pd.DataFrame: Processed clean DataFrame.
    """
    logger.info("Converting sensor temperatures from Kelvin to Celsius...")
    cleaned_df = df.copy()
    
    # Kelvin to Celsius: C = K - 273.15
    cleaned_df["Ambient_Room_Temp_C"] = np.round(cleaned_df["Ambient_Room_Temp_K"] - 273.15, 2)
    cleaned_df["Internal_Device_Temp_C"] = np.round(cleaned_df["Internal_Device_Temp_K"] - 273.15, 2)
    
    # Drop original Kelvin columns to avoid redundancy
    cleaned_df = cleaned_df.drop(columns=["Ambient_Room_Temp_K", "Internal_Device_Temp_K"])
    
    return cleaned_df

def add_synthetic_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Appends synthetic hourly timestamps to the dataset.

    NOTE: The timestamps are generated strictly for demonstrating time-series
    techniques (moving averages, forecasting, etc.) and do not represent historical
    clinical log events.

    Args:
        df: Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with the 'Timestamp' column added.
    """
    logger.info("Appending synthetic hourly timestamps starting from 2026-01-01 00:00:00...")
    df_with_time = df.copy()
    
    # Generate continuous hourly timestamps
    timestamps = pd.date_range(start="2026-01-01 00:00:00", periods=len(df), freq="h")
    df_with_time["Timestamp"] = timestamps
    
    # Ensure Timestamp is the first column for standard log formatting
    cols = ["Timestamp"] + [col for col in df_with_time.columns if col != "Timestamp"]
    df_with_time = df_with_time[cols]
    
    return df_with_time
