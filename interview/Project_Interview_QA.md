# Technical Interview Q&A - Smart ICU Equipment Monitoring Platform

This document prepares the project owner for interviews (such as for the GE HealthCare Data Analyst Internship), providing professional, concise, and technically accurate responses to key questions.

---

### 1. Tell me about this project.
"I developed an end-to-end telemetry analytics and predictive monitoring platform for ICU medical equipment (Ventilators, CT Scanners, and MRI Machines). The project replicates how GE HealthCare clinical systems monitor equipment health, engineering a Python ETL pipeline, establishing an analytical SQLite database, training machine learning classifiers to predict failure risks, and presenting actionable operational metrics in a dashboard."

### 2. What business problem does it solve?
"Unexpected medical equipment downtime costs hospitals millions of dollars in idle staff, cancelled procedures, and outsourced repairs. More critically, equipment failures (like ventilators) threaten patient safety. This project transitions clinical operations from reactive maintenance ('fixing after break') to proactive maintenance ('servicing before failure'), reducing unplanned downtime and optimizing clinical workflows."

### 3. Why did you choose SQLite?
"I chose SQLite because it is a lightweight, serverless database that stores tables in a single file, requiring zero database administration. For an internal analyst prototype or audit, it is highly efficient, supports full ANSI SQL, and integrates directly with Python via standard libraries. It allows fast querying of our 10,000 processed telemetry records without setting up database servers."

### 4. Why Logistic Regression?
"Logistic Regression is a linear classifier that provides direct probabilistic interpretability. By evaluating the coefficients and odds ratios of features like `Temp_Diff` or `Motor_Load_Nm`, we can explain to stakeholders exactly how much a unit increase in a sensor reading raises the likelihood of equipment failure."

### 5. Why Random Forest?
"Random Forest is our primary model. As an ensemble of decision trees, it handles non-linear boundaries and feature interactions (for instance, when a CT scanner has both high operating hours *and* high motor load). It is robust to overfitting, handles class imbalance via balanced sample weights, and provides built-in feature importance rankings."

### 6. Why not Deep Learning?
"Deep learning requires large volumes of data to generalize and behaves as a 'black box,' which is a clinical risk where model decisions must be auditable. Our dataset has 10,000 rows and only 339 failures, making deep learning highly prone to overfitting. Logistic Regression and Random Forest offer higher interpretability, faster training, and sufficient predictive power (Random Forest achieved an ROC-AUC of 0.97)."

### 7. Why generate synthetic timestamps?
"The raw AI4I dataset contains sequential readings but lacks temporal fields. I generated synthetic hourly timestamps starting from `2026-01-01` solely to demonstrate time-series analytics (like calculating rolling means to detect anomalies and trend forecasting). I explicitly documented this simulation to separate it from actual clinical log history."

### 8. Why use heuristic weights for the Failure Risk Index?
"The weights ($30\%$ thermal stress, $30\%$ mechanical load, $40\%$ runtime wear) represent a domain-inspired engineering assumption designed to aggregate multiple sensor dimensions into a single actionable score. They are not clinically validated, but they serve as a benchmark indicator. We validated their utility by checking their strong correlation with true failure outcomes in the dataset."

### 9. How did you validate the data?
"I implemented a automated validation suite in `preprocessing.py` checking:
- **Schema Validation**: Column existence and type correctness.
- **Completeness**: Checking missing value rates (which were 0%).
- **Duplicates**: Checking duplicate row counts (which were 0).
- **Range Validation**: Flagging values violating bounds (e.g., temperatures outside 290K-320K, negative motor loads, speeds > 3000 RPM).
- **Logical Consistency**: Auditing if the overall `Device_Failure` flag aligned with individual failure modes."

### 10. How did you engineer new features?
"I created four primary features:
1. `Temp_Diff`: $T_{\text{internal}} - T_{\text{ambient}}$ to isolate cooling efficiency.
2. `Utilization_Pct`: A power-proxy metric based on fan speed $\times$ load.
3. `Failure_Risk_Index`: Linear combination of thermal, load, and wear stress.
4. `Health_Score`: Inverse of the risk index scaled to 0-100%, divided into Low, Medium, and High risk categorizations."

### 11. Which feature contributed most to failure prediction?
"Feature importance and Permutation Importance evaluations show that `Failure_Risk_Index` is the most critical feature, followed by `Motor_Load_Nm` and `Temp_Diff`. Shuffling the `Failure_Risk_Index` on the test set resulted in the largest drop in model performance, validating our engineered combination of thermal and mechanical stress."

### 12. What SQL analysis was performed?
"I populated a SQLite table `icu_equipment` and ran queries to answer key business questions:
- Ranking categories by total failures (Ventilators/L-type contributed to the highest volume of failures).
- Aggregating average telemetry parameters of failed vs. healthy machines.
- Querying a prioritize list of active Product IDs currently flagged as 'High' risk.
- Analyzing the distribution of specific failure modes (e.g., Overheating vs. Power Supply) across asset classes."

### 13. What business insights were discovered?
"- Failures are heavily concentrated in machines with more than 180 operating hours.
- A critical operational envelope was identified: when `Temp_Diff` exceeds 8.5°C or `Motor_Load` exceeds 55 Nm, failure probability rises exponentially.
- Heat Dissipation Failures (Overheating) and Component Wear are the two leading causes of unplanned downtime."

### 14. What recommendations would you provide to hospital management?
"1. **Scheduled Preventative Maintenance**: Implement an advisory wear threshold at 180 operating hours to check components before they reach the critical 200-hour wear limit.
2. **Real-time Thermal Alerts**: Configure alerts to trigger when `Temp_Diff` exceeds 8.0°C to address cooling fan degradation.
3. **Load Cap Compliance**: Cap continuous motor loads on scanners at 55 Nm to prevent mechanical overstrain.
4. **Triage List Protocol**: Task technicians with checking the daily Top 10 lowest health score machines generated by the platform."

### 15. What are the assumptions and limitations?
"The dataset assumes that the reframed variables represent medical systems, whereas they are sourced from industrial equipment. The timestamps are synthetic, and the Failure Risk Index is based on heuristic weights rather than medical-grade clinical validation. Additionally, the telemetry data is offline rather than streamed."

### 16. How would you improve this system in a production hospital environment?
"I would scale the pipeline by:
- Transitioning the ingestion layer to a real-time message broker like Apache Kafka or AWS Kinesis.
- Mapping sensor telemetry to HL7 or FHIR message formats for Electronic Health Record (EHR) integration.
- Implementing anonymization layers to strip Protected Health Information (PHI) to satisfy HIPAA regulations.
- Migrating SQLite to a cloud data warehouse (like Snowflake or BigQuery) to handle streaming telemetry."

### 17. What did you personally learn while building this project?
"I learned how to bridge the gap between data engineering, machine learning, and business value. Specifically, I learned how to create robust, logged ETL pipelines, validate data quality in structured reports, train predictive models focused on recall (to catch clinical failures), and translate machine learning feature importances into concrete business recommendations that hospital administrators can act on."
