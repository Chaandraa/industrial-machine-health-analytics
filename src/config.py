"""Central configuration module for the Smart ICU Equipment Predictive Monitoring platform.

Contains filesystem paths, clinical reframing maps, data range validation thresholds,
heuristic feature engineering parameters, and machine learning constants.
"""

from pathlib import Path
from typing import Dict, Any, List

# ==============================================================================
# Filesystem Paths
# ==============================================================================
BASE_DIR: Path = Path("C:/Users/HP/Documents/Predictive Maintainace")

# Data Directories
DATA_DIR: Path = BASE_DIR / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
CLEANED_DATA_DIR: Path = DATA_DIR / "cleaned"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"

# Telemetry Files
RAW_DATA_PATH: Path = RAW_DATA_DIR / "predictive_maintainance.csv"
CLEANED_DATA_PATH: Path = CLEANED_DATA_DIR / "cleaned_v1.csv"
PROCESSED_DATA_PATH: Path = PROCESSED_DATA_DIR / "processed_v1.csv"

# Models and Logging
MODELS_DIR: Path = BASE_DIR / "models"
LOGS_DIR: Path = BASE_DIR / "logs"
LOG_FILE_PATH: Path = LOGS_DIR / "platform.log"

# Database
DB_DIR: Path = BASE_DIR / "sql"
DB_PATH: Path = DB_DIR / "healthcare_maintenance.db"

# Ensure dirs exist
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# ==============================================================================
# Clinical Data Dictionary & Column Renaming Mapping
# ==============================================================================
COLUMN_MAPPING: Dict[str, str] = {
    "UDI": "UDI",
    "Product ID": "Product_ID",
    "Type": "Equipment_Type_Code",
    "Air temperature [K]": "Ambient_Room_Temp_K",
    "Process temperature [K]": "Internal_Device_Temp_K",
    "Rotational speed [rpm]": "Cooling_Fan_Speed_RPM",
    "Torque [Nm]": "Motor_Load_Nm",
    "Tool wear [min]": "Operating_Hours",
    "Machine failure": "Device_Failure",
    "TWF": "Failure_Component_Wear",
    "HDF": "Failure_Overheating",
    "PWF": "Failure_Power_Supply",
    "OSF": "Failure_Overload",
    "RNF": "Failure_Random_Hardware"
}

# Equipment Code Mapping
EQUIPMENT_TYPE_MAPPING: Dict[str, str] = {
    "L": "Ventilator",
    "M": "CT Scanner",
    "H": "MRI Machine"
}

# ==============================================================================
# Data Validation Thresholds
# ==============================================================================
# Temperature bounds in Kelvin (matching historical sensor limits)
TEMP_AMBIENT_MIN_K: float = 290.0
TEMP_AMBIENT_MAX_K: float = 310.0

TEMP_INTERNAL_MIN_K: float = 300.0
TEMP_INTERNAL_MAX_K: float = 320.0

# Mechanical bounds
FAN_SPEED_MIN_RPM: float = 1000.0
FAN_SPEED_MAX_RPM: float = 3000.0

MOTOR_LOAD_MIN_NM: float = 0.0
MOTOR_LOAD_MAX_NM: float = 100.0

OPERATING_HOURS_MIN: float = 0.0
OPERATING_HOURS_MAX: float = 300.0

# ==============================================================================
# Feature Engineering Parameters (Heuristic Assumptions)
# ==============================================================================
# Scaling components for the Failure Risk Index (weights must sum to 1.0)
RISK_TEMP_DIFF_WEIGHT: float = 0.3
RISK_MOTOR_LOAD_WEIGHT: float = 0.3
RISK_WEAR_WEIGHT: float = 0.4

# Heuristic denominators representing maximum normal operational envelopes
NORMAL_TEMP_DIFF_LIMIT: float = 15.0  # Kelvin/Celsius diff
NORMAL_MOTOR_LOAD_LIMIT: float = 80.0  # Nm torque
NORMAL_WEAR_LIMIT: float = 250.0       # hours

# Health Score limits
HEALTH_SCORE_HIGH_RISK_THRESHOLD: float = 60.0
HEALTH_SCORE_MED_RISK_THRESHOLD: float = 80.0

# ==============================================================================
# Machine Learning Hyperparameters
# ==============================================================================
RANDOM_STATE: int = 42
TEST_SIZE: float = 0.2

# Models to Train
ML_MODELS_CONFIG: Dict[str, Dict[str, Any]] = {
    "LogisticRegression": {
        "max_iter": 1000,
        "C": 1.0,
        "solver": "liblinear",
        "random_state": RANDOM_STATE
    },
    "RandomForest": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "random_state": RANDOM_STATE,
        "class_weight": "balanced"
    },
    "XGBoost": {
        "n_estimators": 100,
        "max_depth": 5,
        "learning_rate": 0.1,
        "random_state": RANDOM_STATE,
        "use_label_encoder": False,
        "eval_metric": "logloss"
    }
}
