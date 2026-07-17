# Data Dictionary - Smart ICU Equipment Monitoring Platform

This document describes the schema of the final processed dataset (`data/processed/processed_v1.csv`) used by the machine learning pipeline and SQLite database.

---

| Column Name | Data Type | Unit | Description | Original Source Column | Business / Clinical Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Timestamp** | DATETIME | - | Synthetic date and hour of sensor reading. | *Generated* | Used for demonstrating time-series trends and rolling statistics. *Not a real historical log timestamp.* |
| **UDI** | INTEGER | ID | Unique row database identifier. | UDI | Primary Key. Unique index identifier for SQL table operations. |
| **Product_ID** | TEXT | String | Unique manufacturer hardware serial number. | Product ID | Asset identifier. Code prefix designates quality class: L (Low), M (Medium), H (High). |
| **Equipment_Type_Code** | TEXT | Category | Original industrial category (L, M, H). | Type | Operational tier code. Reframed into Equipment Categories. |
| **Equipment_Category** | TEXT | Category | Reframed device type: Ventilator, CT Scanner, or MRI Machine. | *Derived from Type* | **L** -> Ventilator (High volume)<br>**M** -> CT Scanner (Medium volume)<br>**H** -> MRI Machine (High criticality, complex cooling). |
| **Ambient_Room_Temp_C** | REAL | °C | Ambient room temperature surrounding the equipment. | Air temperature [K] | Monitored to verify ICU climate control compliance. Converted from Kelvin. |
| **Internal_Device_Temp_C**| REAL | °C | Internal temperature of the device housing. | Process temperature [K] | Sensor value checking internal heat levels. Converted from Kelvin. |
| **Temp_Diff** | REAL | °C | Differential: Internal Device Temp - Ambient Room Temp. | *Derived* | Heat dissipation efficiency proxy. A rising gradient signals cooling failure. |
| **Cooling_Fan_Speed_RPM** | INTEGER | RPM | Rotational speed of the internal cooling subsystem. | Rotational speed [rpm] | Monitored cooling mechanical subsystem rate. |
| **Motor_Load_Nm** | REAL | Nm | Mechanical torque load on moving components. | Torque [Nm] | Gantry rotational load for CT, cryogenic pump load for MRI, blower load for Ventilator. |
| **Operating_Hours** | INTEGER | Hours | Cumulative hours since the last overhaul. | Tool wear [min] | Wear indicator tracking runtime hours since last service dispatch. |
| **Device_Failure** | INTEGER | Binary | Target: 0 = Healthy, 1 = Failed. | Machine failure | Critical unplanned equipment outage flag. |
| **Failure_Component_Wear**| INTEGER | Binary | Wear-out failure flag. | TWF | Cumulative operational hours exceeded service life. |
| **Failure_Overheating** | INTEGER | Binary | Overheating failure flag. | HDF | Thermal dissipation failure (high Temp_Diff and slow fan). |
| **Failure_Power_Supply** | INTEGER | Binary | Power supply outage failure flag. | PWF | Electrical draw mismatch or backup battery collapse. |
| **Failure_Overload** | INTEGER | Binary | Physical overload failure flag. | OSF | Mechanical strain boundary exceeded (load x runtime). |
| **Failure_Random_Hardware**| INTEGER | Binary | Random hardware failure flag. | RNF | Non-deterministic sensor/component glitch. |
| **Age_Group** | TEXT | Category | Categorical age grouping: Low, Medium, High. | *Derived from Tool wear* | Run time categorization: Low (0-100 hrs), Medium (101-200 hrs), High (201-300 hrs). |
| **Utilization_Pct** | REAL | % | Estimated load capacity. | *Derived from speed & load*| Power-based estimate representing work intensity. |
| **Failure_Risk_Index** | REAL | Score | Combined failure risk score (0.0 to 1.0). | *Derived* | Linear combination of thermal, load, and wear stress (weights: 30%, 30%, 40%). |
| **Health_Score** | REAL | % | Standardized device health percentage (0-100%). | *Derived* | Heuristic health percentage (`100.0 - Risk_Index * 100`). |
| **Maintenance_Risk** | TEXT | Category | Risk categories: Low, Medium, High. | *Derived* | Actionable dispatch categories: Low (Health >= 80), Medium (60-79), High (< 60). |
