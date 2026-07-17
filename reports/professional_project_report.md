# Executive Project Report: Smart ICU Equipment Predictive Monitoring

**Document Class**: Clinical Engineering Operations & Predictive Analytics  
**Organization**: GE HealthCare Capstone Project  
**Author**: Data Engineering & Analytics Team  
**Date**: July 2026

---

## 1. Executive Summary
Modern hospitals lose millions of dollars annually due to unplanned medical equipment downtime, resulting in delayed procedures, increased labor costs, and reduced patient access. More critically, unexpected equipment failure in Intensive Care Units (ICUs) directly impacts patient safety.

This project implements an end-to-end telemetry analytics solution. By reframing a 10,000-record sensor dataset into clinical categories (Ventilators, CT Scanners, and MRI Machines) and applying data engineering, SQL analysis, and machine learning, we identify key failure modes and build an alert dashboard. Our primary classifier (Random Forest) achieves $97.5\%$ accuracy and $88.2\%$ recall, allowing clinical teams to catch equipment failures before they manifest. Based on the findings, we recommend scheduled maintenance at 180 operating hours and load-capping rotating gantries at 55 Nm, reducing unplanned outages.

---

## 2. Business Problem Statement
Clinical operations depend on high-availability assets. Unplanned downtime has severe operational and financial impacts:
1. **Clinical Bottlenecks**: Procedural cancellations due to offline CT scanners delay diagnoses.
2. **High Repair Surcharges**: Emergency vendor callouts cost up to $300\%$ more than scheduled maintenance.
3. **Patient Risk**: Immediate collapse of life-support equipment (e.g. ventilators) requires emergency overrides.

### Project Objectives
- Ingest and validate sensor telemetry logs.
- Identify the physical and mechanical boundaries causing failure.
- Load clean records into an index-optimized database for daily queries.
- Build predictive models prioritising recall to identify failing assets.
- Deliver concrete business recommendations to hospital administration.

---

## 3. Dataset & Data Quality Assessment
We analyzed 10,000 sensor observations. Each row represents a telemetry window containing ambient temperature, device temperature, rotational fan speed, mechanical load, and operating wear hours.

### Data Quality Audit Summary
An automated audit was executed inside `preprocessing.py` and output to `data_quality_report_v1.json`:
* **Completeness**: $100\%$ completeness rate across all columns. There are zero null values.
* **Uniqueness**: Zero duplicate rows found.
* **Range Validation**:
  - Fan speeds conform to the $1000 - 3000\text{ RPM}$ standard.
  - Temperature levels are consistent with typical operating environments ($290\text{ K} - 320\text{ K}$).
  - Motor load and operating hour values fall within expected mechanical margins ($0-100\text{ Nm}$ and $0-300\text{ hours}$).
* **Logical Consistency Check**: Mismatch analysis between the binary `Device_Failure` target and sub-failure mode flags (`Failure_Overheating`, `Failure_Component_Wear`, etc.) revealed 9 failures in the raw dataset that did not have specific sub-modes flagged. We preserve these as general hardware failures.

---

## 4. Methodology & Engineering Pipeline
The project workflow is structured into a modular Python library:
1. **Ingestion**: Loading the raw sensor CSV using `src.data_loader`.
2. **Preprocessing**: Validating columns, converting temperatures from Kelvin to Celsius, mapping L/M/H codes to Ventilators, CT Scanners, and MRI Machines, and adding synthetic hourly timestamps. Output saved to `data/cleaned/cleaned_v1.csv`.
3. **Feature Engineering**: Creating `Temp_Diff` (internal - ambient temp), `Utilization_Pct` (speed x load), `Failure_Risk_Index` (linear combination), and `Health_Score` (0-100%). Output saved to `data/processed/processed_v1.csv`.
4. **Database Storage**: Initializing SQLite tables with indexes and loading processed records.
5. **Machine Learning**: Partitioning data into stratified train/test sets ($80/20$), training Logistic Regression and Random Forest models, and exporting metadata.
6. **Inference**: Loading models into Streamlit (`app.py`) for live prediction reports.

---

## 5. SQL Operational Analytics
Cleaned data was inserted into SQLite database `sql/healthcare_maintenance.db`. We executed reporting queries from `sql/queries.sql` to answer core questions:

* **BQ1: Failure Distribution**:
  - **Ventilators** (L-Type): 235 failures ($3.36\%$ rate).
  - **CT Scanners** (M-Type): 83 failures ($3.46\%$ rate).
  - **MRI Machines** (H-Type): 21 failures ($3.50\%$ rate).
  - *Insight*: Total failure count is dominated by ventilators due to their high volume ($70\%$ of inventory), but baseline failure rates are statistically uniform across categories.

* **BQ2: Operational Telemetry Baselines**:
  - Healthy machines operate at an average temperature difference of **3.0°C**, motor load of **39.6 Nm**, and **107.5 operating hours**.
  - Failed machines show a stark telemetry profile: average temperature difference of **8.6°C** (thermal stress), motor load of **55.0 Nm** (high overload stress), and **119.5 operating hours** (cumulative wear).
  - Average Health Score is **95.8%** for healthy machines and **59.8%** for failed machines.

---

## 6. Machine Learning & Model Explainability

We trained Logistic Regression, Random Forest, and XGBoost models.

### Performance Benchmarks
| Metric | Logistic Regression | Random Forest (Primary) | XGBoost (Comparison) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 96.95% | 97.50% | 98.70% |
| **Precision**| 66.67% | 58.82% | 88.89% |
| **Recall**   | 20.59% | 88.24% | 70.59% |
| **F1 Score** | 31.46% | 70.59% | 78.69% |
| **ROC-AUC**  | 0.9296 | 0.9758 | 0.9765 |

### Clinically Aligned Model Selection
We select **Random Forest** as the production classifier despite XGBoost having a higher F1-score. In clinical settings, **Recall is the priority metric**. Missing a failing device (False Negative) can result in unplanned procedure cancellations or patient risk. Random Forest achieves a recall of **88.24%** (catching 60 out of 68 failures in the test set) compared to XGBoost's recall of $70.59\%$.

### Model Explainability Analysis
To satisfy clinical transparency, we run Feature Importance and Permutation Importance:
1. **Random Forest Feature Importance**:
   - `Failure_Risk_Index`: $50.2\%$
   - `Motor_Load_Nm`: $17.6\%$
   - `Temp_Diff`: $14.1\%$
   - `Cooling_Fan_Speed_RPM`: $9.3\%$
   - `Operating_Hours`: $5.4\%$
2. **Permutation Importance**:
   - Shuffling `Failure_Risk_Index` on the test set resulted in the largest drop in classification accuracy ($0.038$), confirming its role as our strongest predictor.
   - *Interpretation*: The combination of mechanical torque load and temperature gradient drives failures. These findings guide our maintenance recommendations.

---

## 7. Business Recommendations

### 1. Preventative Maintenance Scheduling (Wear Window)
* **Finding**: Outages occur primarily in machines with more than 180 operating hours.
* **Business Impact**: Allowing machines to operate past 200 hours increases outage probability, causing procedurial delays and increasing emergency repair costs by $300\%$.
* **Recommendation**: Set a mandatory preventative maintenance checkpoint at **180 operating hours**. Warn technicians at 160 hours to prepare replacement parts.

### 2. Thermal Dissipation Alerts
* **Finding**: Overheating failures cluster when the Temperature Difference (`Temp_Diff`) exceeds **8.5°C**.
* **Business Impact**: Sudden thermal shutdowns force ventilators offline, threatening patient lives and requiring urgent technician dispatches.
* **Recommendation**: Configure real-time telemetry threshold triggers on all assets. Alert technicians if `Temp_Diff` exceeds **8.0°C** to schedule filter cleanings or coolant refills before a thermal shutdown occurs.

### 3. Load Capping on Rotating Components
* **Finding**: Motor Load (Torque) values exceeding **55 Nm** are heavily associated with Overstrain failures.
* **Business Impact**: Sustained high loads accelerate bearing wear and rotor fatigue, requiring costly gantry replacements.
* **Recommendation**: Cap routine operating loads on rotating components at **55 Nm**. Require a cooldown cycle immediately following any high-load clinical procedures.

### 4. Triage Checklist Protocol
* **Finding**: The engineered `Health_Score` successfully separates failing assets (averaging 59.8) from healthy ones (averaging 95.8).
* **Business Impact**: Routine service schedules often prioritize healthy machines, leaving failing assets unaddressed.
* **Recommendation**: Integrate the SQLite-generated BQ3 query ("High Maintenance Risk Priority List") into daily task lists. Require technicians to inspect assets dropping below a **60.0 Health Score** within 4 hours.

---

## 8. Future Scope & System Scalability
To transition this prototype to a hospital environment, we propose:
1. **HL7/FHIR Ingestion**: Integrate telemetry with hospital data networks using FHIR resources.
2. **Streaming Pipeline**: Transition from batch CSVs to a real-time Kafka and Spark streaming architecture for instant failure detection.
3. **Anonymization Layers**: Implement PHI stripping filters to ensure compliance with HIPAA regulations.
