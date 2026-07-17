"""ETL pipeline execution script.

Orchestrates the Smart ICU Equipment ETL process:
1. Ingestion of raw industrial telemetry CSV.
2. Runs validation checks and outputs a Data Quality report.
3. Cleans variables, converts temperatures, and outputs cleaned_v1.csv.
4. Engineers features (utilization, health index) and outputs processed_v1.csv.
5. Loads data into SQLite database using sql/schema.sql.
"""

import os
import json
import sqlite3
import pandas as pd
from src.config import (
    RAW_DATA_PATH,
    CLEANED_DATA_PATH,
    PROCESSED_DATA_PATH,
    DB_PATH,
    DB_DIR
)
from src.data_loader import load_raw_telemetry
from src.preprocessing import (
    run_data_quality_report,
    rename_and_map_columns,
    convert_units_and_clean,
    add_synthetic_timestamps
)
from src.feature_engineering import run_feature_engineering_pipeline
from src.utils import get_logger, get_db_connection

logger = get_logger("src.pipeline")

def execute_etl() -> None:
    """Executes the complete end-to-end ETL pipeline."""
    logger.info("==================================================")
    logger.info("Starting Smart ICU Equipment ETL Pipeline Run")
    logger.info("==================================================")
    
    # 1. Ingest Raw Telemetry
    raw_df = load_raw_telemetry(RAW_DATA_PATH)
    
    # 2. Run Data Quality Analysis
    dq_report = run_data_quality_report(raw_df)
    dq_report_path = os.path.join(os.path.dirname(CLEANED_DATA_PATH), "data_quality_report_v1.json")
    with open(dq_report_path, "w", encoding="utf-8") as f:
        json.dump(dq_report, f, indent=2)
    logger.info(f"Data Quality Report saved to: {dq_report_path}")
    
    # Print high-level metrics to log
    logger.info(f"Completeness Rate: {dq_report['completeness_percentage']:.2f}%")
    logger.info(f"Duplicate rows found: {dq_report['duplicates']['duplicate_rows_count']}")
    
    # 3. Clean and map columns
    mapped_df = rename_and_map_columns(raw_df)
    cleaned_df = convert_units_and_clean(mapped_df)
    
    # Save Cleaned v1 CSV
    os.makedirs(os.path.dirname(CLEANED_DATA_PATH), exist_ok=True)
    cleaned_df.to_csv(CLEANED_DATA_PATH, index=False)
    logger.info(f"Cleaned dataset saved to: {CLEANED_DATA_PATH}")
    
    # 4. Feature Engineering
    processed_df = run_feature_engineering_pipeline(cleaned_df)
    processed_df = add_synthetic_timestamps(processed_df)
    
    # Save Processed v1 CSV
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    processed_df.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info(f"Processed feature-engineered dataset saved to: {PROCESSED_DATA_PATH}")
    
    # 5. Load to SQLite
    load_to_sqlite(processed_df)
    
    logger.info("==================================================")
    logger.info("Smart ICU Equipment ETL Pipeline Completed Successfully")
    logger.info("==================================================")

def load_to_sqlite(df: pd.DataFrame) -> None:
    """Loads the processed DataFrame into SQLite database.

    Args:
        df: Input processed DataFrame.
    """
    logger.info("Initiating SQLite database loading phase...")
    schema_file = os.path.join(DB_DIR, "schema.sql")
    
    # Connect and setup schema
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        logger.info(f"Reading database schema from: {schema_file}")
        with open(schema_file, "r") as f:
            schema_ddl = f.read()
        
        # Execute DDL
        cursor.executescript(schema_ddl)
        conn.commit()
        logger.info("Database tables and indexes created successfully.")
        
        # Insert records in chunks
        logger.info(f"Inserting {len(df)} records into table 'icu_equipment'...")
        # Convert categoricals or datetimes as necessary for sqlite
        df_db = df.copy()
        df_db["Timestamp"] = df_db["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df_db["Age_Group"] = df_db["Age_Group"].astype(str)
        
        df_db.to_sql("icu_equipment", conn, if_exists="append", index=False)
        conn.commit()
        logger.info("Successfully loaded all records into SQLite database.")
        
        # Validate count
        cursor.execute("SELECT COUNT(*) FROM icu_equipment;")
        inserted_count = cursor.fetchone()[0]
        logger.info(f"Verification query count: {inserted_count} records active in DB.")
        
    except Exception as e:
        logger.error(f"Error during SQLite database setup and loading: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    execute_etl()
