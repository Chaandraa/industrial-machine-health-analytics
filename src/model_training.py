"""Model training, evaluation, and explainability script.

Trains the target classifiers (Logistic Regression, Random Forest, and XGBoost),
evaluates them on standard classification metrics, computes feature and permutation
importance metrics for explainability, and saves the serialization objects and metadata.
"""

import os
import json
import joblib
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)
import xgboost as xgb
from src.config import (
    PROCESSED_DATA_PATH,
    MODELS_DIR,
    RANDOM_STATE,
    TEST_SIZE,
    ML_MODELS_CONFIG
)
from src.utils import get_logger

logger = get_logger("src.model_training")

def train_and_evaluate_models() -> None:
    """Trains, saves, and evaluates classification models."""
    logger.info("==================================================")
    logger.info("Starting Machine Learning Pipeline Run")
    logger.info("==================================================")
    
    # 1. Load Processed Data
    if not os.path.exists(PROCESSED_DATA_PATH):
        raise FileNotFoundError(f"Processed features file not found at: {PROCESSED_DATA_PATH}")
        
    df = pd.read_csv(PROCESSED_DATA_PATH)
    logger.info(f"Loaded processed dataset. Shape: {df.shape}")
    
    # 2. Extract Features and Labels
    features = [
        "Ambient_Room_Temp_C", 
        "Internal_Device_Temp_C", 
        "Cooling_Fan_Speed_RPM", 
        "Motor_Load_Nm", 
        "Operating_Hours", 
        "Temp_Diff", 
        "Utilization_Pct", 
        "Failure_Risk_Index"
    ]
    X = df[features]
    y = df["Device_Failure"]
    
    # 3. Stratified Partitioning (Preserves target ratio in training/testing)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=TEST_SIZE, 
        random_state=RANDOM_STATE, 
        stratify=y
    )
    logger.info(f"Training set: {X_train.shape}, Testing set: {X_test.shape}")
    
    # Dictionary to collect evaluation metadata
    evaluation_metadata = {}
    
    # Train Models
    for model_name, config in ML_MODELS_CONFIG.items():
        logger.info(f"Training model: {model_name}...")
        
        if model_name == "LogisticRegression":
            model = LogisticRegression(**config)
        elif model_name == "RandomForest":
            model = RandomForestClassifier(**config)
        elif model_name == "XGBoost":
            model = xgb.XGBClassifier(**config)
        else:
            logger.warning(f"Unrecognized model type configuration: {model_name}")
            continue
            
        # Fit Model
        model.fit(X_train, y_train)
        
        # Save Model Binary
        model_filename = f"{model_name.lower()}_v1.joblib"
        model_path = MODELS_DIR / model_filename
        joblib.dump(model, model_path)
        logger.info(f"Saved model binary file to: {model_path}")
        
        # Run Inferences
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred
        
        # Calculate Metrics
        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "f1_score": float(f1_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_prob))
        }
        
        logger.info(f"Evaluation Metrics for {model_name}:")
        for metric_name, val in metrics.items():
            logger.info(f"  {metric_name}: {val:.4f}")
        
        # Compute Explainability Metrics for Random Forest (our production model)
        feat_imp = {}
        perm_imp_dict = {}
        if model_name == "RandomForest":
            logger.info("Computing Feature Importances for RandomForest...")
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1]
            for f in range(X.shape[1]):
                feat_imp[features[indices[f]]] = float(importances[indices[f]])
                
            logger.info("Computing Permutation Importances for RandomForest (on test set)...")
            perm_results = permutation_importance(
                model, X_test, y_test, 
                n_repeats=10, 
                random_state=RANDOM_STATE
            )
            for i in perm_results.importances_mean.argsort()[::-1]:
                perm_imp_dict[features[i]] = float(perm_results.importances_mean[i])
                
        # Append to metadata
        evaluation_metadata[model_name] = {
            "model_name": model_name,
            "version": "v1",
            "training_timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"),
            "features_used": features,
            "hyperparameters": {k: (str(v) if not isinstance(v, (int, float, bool, list, dict)) else v) for k, v in config.items()},
            "metrics": metrics,
            "feature_importances": feat_imp if model_name == "RandomForest" else None,
            "permutation_importances": perm_imp_dict if model_name == "RandomForest" else None
        }
        
    # Write JSON metadata
    metadata_path = MODELS_DIR / "model_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_metadata, f, indent=2)
    logger.info(f"Serliazed model metadata saved to: {metadata_path}")
    
    logger.info("==================================================")
    logger.info("Machine Learning Pipeline Completed Successfully")
    logger.info("==================================================")

if __name__ == "__main__":
    train_and_evaluate_models()
