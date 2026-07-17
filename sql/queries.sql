-- sql/queries.sql
-- Operational queries for the Smart ICU Equipment Monitoring & Analytics Platform

-- BQ1: Which equipment type fails most frequently?
-- Focuses on totaling failures and computing percentages to rank categories.
SELECT 
    Equipment_Category, 
    COUNT(*) AS Total_Assets, 
    SUM(Device_Failure) AS Failure_Count,
    ROUND(CAST(SUM(Device_Failure) AS REAL) / COUNT(*) * 100, 2) AS Failure_Rate_Pct
FROM 
    icu_equipment
GROUP BY 
    Equipment_Category
ORDER BY 
    Failure_Count DESC;

-- BQ2: What is the average operational telemetry (temperatures, speed, load) of failed vs. healthy machines?
-- Helps clinical engineers understand the baseline values associated with failure states.
SELECT 
    Device_Failure,
    COUNT(*) AS Count,
    ROUND(AVG(Ambient_Room_Temp_C), 2) AS Avg_Ambient_Temp_C,
    ROUND(AVG(Internal_Device_Temp_C), 2) AS Avg_Internal_Temp_C,
    ROUND(AVG(Temp_Diff), 2) AS Avg_Temp_Diff_C,
    ROUND(AVG(Cooling_Fan_Speed_RPM), 2) AS Avg_Fan_Speed_RPM,
    ROUND(AVG(Motor_Load_Nm), 2) AS Avg_Motor_Load_Nm,
    ROUND(AVG(Operating_Hours), 2) AS Avg_Operating_Hours,
    ROUND(AVG(Health_Score), 2) AS Avg_Health_Score
FROM 
    icu_equipment
GROUP BY 
    Device_Failure;

-- BQ3: Which specific devices (Product IDs) currently have a 'High' maintenance risk and should be prioritized?
-- Serves as the actionable service checklist for hospital technicians.
SELECT 
    Product_ID, 
    Equipment_Category, 
    Health_Score, 
    Operating_Hours, 
    Motor_Load_Nm, 
    Temp_Diff, 
    Maintenance_Risk
FROM 
    icu_equipment
WHERE 
    Maintenance_Risk = 'High'
ORDER BY 
    Health_Score ASC
LIMIT 15;

-- BQ4: What is the breakdown of failure modes (Overheating vs. Power Supply vs. Component Wear) across different equipment categories?
-- Helps hospital administration plan spare parts inventory and vendor service contracts.
SELECT 
    Equipment_Category, 
    COUNT(*) AS Total_Devices,
    SUM(Device_Failure) AS Total_Failures,
    SUM(Failure_Component_Wear) AS Component_Wear_Failures,
    SUM(Failure_Overheating) AS Overheating_Failures,
    SUM(Failure_Power_Supply) AS Power_Supply_Failures,
    SUM(Failure_Overload) AS Overload_Failures,
    SUM(Failure_Random_Hardware) AS Random_Hardware_Failures
FROM 
    icu_equipment
GROUP BY 
    Equipment_Category;
