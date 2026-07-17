-- SQL schema for the Smart ICU Equipment Predictive Monitoring & Analytics Platform.
-- Table: icu_equipment

DROP TABLE IF EXISTS icu_equipment;

CREATE TABLE icu_equipment (
    Timestamp DATETIME NOT NULL,
    UDI INTEGER PRIMARY KEY,
    Product_ID TEXT NOT NULL,
    Equipment_Type_Code TEXT NOT NULL,
    Equipment_Category TEXT NOT NULL,
    Cooling_Fan_Speed_RPM INTEGER NOT NULL,
    Motor_Load_Nm REAL NOT NULL,
    Operating_Hours INTEGER NOT NULL,
    Device_Failure INTEGER NOT NULL,
    Failure_Component_Wear INTEGER NOT NULL,
    Failure_Overheating INTEGER NOT NULL,
    Failure_Power_Supply INTEGER NOT NULL,
    Failure_Overload INTEGER NOT NULL,
    Failure_Random_Hardware INTEGER NOT NULL,
    Ambient_Room_Temp_C REAL NOT NULL,
    Internal_Device_Temp_C REAL NOT NULL,
    Temp_Diff REAL NOT NULL,
    Age_Group TEXT NOT NULL,
    Utilization_Pct REAL NOT NULL,
    Failure_Risk_Index REAL NOT NULL,
    Health_Score REAL NOT NULL,
    Maintenance_Risk TEXT NOT NULL
);

-- Indexing for optimized analytical performance
CREATE INDEX IF NOT EXISTS idx_equipment_category ON icu_equipment (Equipment_Category);
CREATE INDEX IF NOT EXISTS idx_device_failure ON icu_equipment (Device_Failure);
CREATE INDEX IF NOT EXISTS idx_maintenance_risk ON icu_equipment (Maintenance_Risk);
CREATE INDEX IF NOT EXISTS idx_product_id ON icu_equipment (Product_ID);
CREATE INDEX IF NOT EXISTS idx_timestamp ON icu_equipment (Timestamp);
