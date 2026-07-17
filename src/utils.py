"""Utility functions for logging and database connectivity.

Provides a standardized logging setup that outputs to both a log file and the console,
and helper functions to manage SQLite database transactions.
"""

import logging
import sqlite3
from logging.handlers import RotatingFileHandler
import os
import pandas as pd
from typing import Optional
from src.config import LOG_FILE_PATH, DB_PATH

def get_logger(name: str) -> logging.Logger:
    """Configures and returns a named logger with rotating file and stream handlers.

    Args:
        name: The name of the logger (typically __name__).

    Returns:
        logging.Logger: Preconfigured logger instance.
    """
    logger = logging.getLogger(name)
    
    # If logger is already configured, return it to prevent duplicate logs
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler (rotating file log, max 10MB per file, keeping 5 backups)
    try:
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback if file handler fails (e.g. permission error)
        logger.warning(f"Could not initialize file logging handler: {e}")
        
    return logger

# Initialize base logger
logger = get_logger("src.utils")

def get_db_connection() -> sqlite3.Connection:
    """Establishes and returns a connection to the SQLite database.

    Returns:
        sqlite3.Connection: SQLite database connection object.
    """
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        # Enable foreign key support and column name access in row rows
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to SQLite database at {DB_PATH}: {e}")
        raise e

def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    """Executes an SQL query and returns results in a Pandas DataFrame.

    Args:
        query: SQL string query to execute.
        params: Bind parameters for the query.

    Returns:
        pd.DataFrame: Query results as a DataFrame.
    """
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        logger.error(f"Database query execution failed: {e}\nQuery: {query}")
        raise e
    finally:
        conn.close()
