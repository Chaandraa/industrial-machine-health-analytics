"""Feature engineering module for calculating clinical monitoring indicators.

Computes metrics representing thermal stress, work intensity, and cumulative wear,
translating telemetry into actionable equipment health score cards.
"""

import pandas as pd
import numpy as np
from src.config import (
    RISK_TEMP_DIFF_WEIGHT, RISK_MOTOR_LOAD_WEIGHT, RISK_WEAR_WEIGHT,
    NORMAL_TEMP_DIFF_LIMIT, NORMAL_MOTOR_LOAD_LIMIT, NORMAL_WEAR_LIMIT,
    HEALTH_SCORE_HIGH_RISK_THRESHOLD, HEALTH_SCORE_MED_RISK_THRESHOLD
)
from src.utils import get_logger

logger = get_logger("src.feature_engineering")

def calculate_temperature_difference(df: pd.DataFrame) -> pd.Series:
    """Calculates the temperature difference (Temp_Diff).

    Formula: Temp_Diff = Internal_Device_Temp_C - Ambient_Room_Temp_C
    Justification: High difference indicates heat dissipation failure (e.g. failing fan).

    Args:
        df: Input clean DataFrame.

    Returns:
        pd.Series: Temperature differences.
    """
    logger.info("Calculating Temperature Difference...")
    return df["Internal_Device_Temp_C"] - df["Ambient_Room_Temp_C"]

def calculate_utilization_percentage(df: pd.DataFrame) -> pd.Series:
    """Calculates the device utilization percentage.

    Formula: min(100.0, (Cooling_Fan_Speed_RPM * Motor_Load_Nm) / 60000.0 * 100.0)
    Justification: Power consumption is proportional to torque (load) x speed.
    Product of speed and torque tracks operational stress intensity.

    Args:
        df: Input clean DataFrame.

    Returns:
        pd.Series: Utilization percentage values.
    """
    logger.info("Calculating Equipment Utilization percentage...")
    power_proxy = df["Cooling_Fan_Speed_RPM"] * df["Motor_Load_Nm"]
    # Normalize with 60,000 as proxy limit and cap at 100%
    util_pct = (power_proxy / 60000.0) * 100.0
    return np.minimum(100.0, util_pct)

def calculate_failure_risk_index(df: pd.DataFrame) -> pd.Series:
    """Calculates the heuristic Failure Risk Index.

    Formula:
        Risk = 0.3 * (Temp_Diff / 15.0) + 0.3 * (Motor_Load_Nm / 80.0) + 0.4 * (Operating_Hours / 250.0)
        
    WARNING: The weights (30% thermal stress, 30% mechanical load, 40% operating wear)
    are domain-inspired assumptions for demonstrating analytical methods.
    They are NOT clinically validated or certified.

    Args:
        df: Input DataFrame containing Temp_Diff, Motor_Load_Nm, and Operating_Hours.

    Returns:
        pd.Series: Heuristic risk index values (scaled 0 to 1).
    """
    logger.info("Calculating Failure Risk Index (using heuristic weights)...")
    
    # Check if dependencies exist
    if "Temp_Diff" not in df.columns:
        raise ValueError("Temp_Diff must be calculated before computing the Failure Risk Index.")
        
    term_temp = df["Temp_Diff"] / NORMAL_TEMP_DIFF_LIMIT
    term_load = df["Motor_Load_Nm"] / NORMAL_MOTOR_LOAD_LIMIT
    term_wear = df["Operating_Hours"] / NORMAL_WEAR_LIMIT
    
    # Weighted linear combination
    risk_index = (
        (RISK_TEMP_DIFF_WEIGHT * term_temp) +
        (RISK_MOTOR_LOAD_WEIGHT * term_load) +
        (RISK_WEAR_WEIGHT * term_wear)
    )
    
    # Ensure risk index lies between 0 and 1
    return np.clip(risk_index, 0.0, 1.0)

def categorize_maintenance_risk(health_score: pd.Series) -> pd.Series:
    """Categorizes maintenance risk based on the Health Score.

    Low (Health >= 80), Medium (60 <= Health < 80), High (Health < 60).

    Args:
        health_score: Pandas Series containing Health Scores.

    Returns:
        pd.Series: Categorical series representing maintenance risk classes.
    """
    logger.info("Categorizing equipment Maintenance Risk levels...")
    conditions = [
        health_score >= HEALTH_SCORE_MED_RISK_THRESHOLD,
        (health_score >= HEALTH_SCORE_HIGH_RISK_THRESHOLD) & (health_score < HEALTH_SCORE_MED_RISK_THRESHOLD),
        health_score < HEALTH_SCORE_HIGH_RISK_THRESHOLD
    ]
    choices = ["Low", "Medium", "High"]
    return pd.Series(np.select(conditions, choices, default="Low"), index=health_score.index)

def run_feature_engineering_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Executes the complete feature engineering pipeline.

    Calculates Temp_Diff, Utilization_Pct, Failure_Risk_Index, Health_Score,
    Maintenance_Risk, and Age_Group.

    Args:
        df: Clean input DataFrame.

    Returns:
        pd.DataFrame: Feature engineered DataFrame.
    """
    logger.info("Executing comprehensive Feature Engineering Pipeline...")
    engineered_df = df.copy()
    
    # 1. Temperature Difference
    engineered_df["Temp_Diff"] = np.round(calculate_temperature_difference(engineered_df), 2)
    
    # 2. Equipment Age Group
    logger.info("Slicing cumulative Operating Hours into Age Groups (Low/Medium/High)...")
    engineered_df["Age_Group"] = pd.cut(
        engineered_df["Operating_Hours"],
        bins=[0, 100, 200, 300],
        labels=["Low", "Medium", "High"],
        include_lowest=True
    )
    
    # 3. Utilization Pct
    engineered_df["Utilization_Pct"] = np.round(calculate_utilization_percentage(engineered_df), 2)
    
    # 4. Failure Risk Index
    engineered_df["Failure_Risk_Index"] = np.round(calculate_failure_risk_index(engineered_df), 4)
    
    # 5. Health Score (100 - Risk * 100)
    logger.info("Computing asset Health Scores...")
    engineered_df["Health_Score"] = np.round(100.0 - (engineered_df["Failure_Risk_Index"] * 100.0), 2)
    
    # 6. Maintenance Risk Category
    engineered_df["Maintenance_Risk"] = categorize_maintenance_risk(engineered_df["Health_Score"])
    
    logger.info("Feature engineering pipeline completed successfully.")
    return engineered_df
