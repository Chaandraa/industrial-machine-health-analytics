# Decision Log - Smart ICU Equipment Monitoring Platform

This document logs the core architectural and modeling decisions made during the design and development of the Capstone project.

---

## 1. Primary Tech Stack Selection
- **Decision**: Python for the data pipeline and machine learning; SQLite for structured database queries; Streamlit for the operational dashboard mockup.
- **Rationale**: Python provides industry-standard libraries (Scikit-Learn, Pandas) for building clean, reproducible ETL and ML pipelines. SQLite is serverless, requires zero configuration, and operates entirely in-memory or as a single file, making it perfect for lightweight analyst audits. Streamlit allows rapid deployment of an interactive, code-driven UI without front-end overhead.
- **Trade-offs**: SQLite lacks advanced concurrency controls and complex window functions compared to PostgreSQL, but matches the scope of local analyst capstones.

## 2. Industrial-to-Clinical Dataset Reframing
- **Decision**: Map AI4I industrial variables directly to clinical ICU device telemetry (e.g., Tool Wear to Operating Hours, Process Temp to Internal Device Temp).
- **Rationale**: Industrial predictive maintenance shares direct mathematical mappings with medical device monitoring (both track thermal stress, mechanical speed, torque loads, and runtime fatigue). Mapping the dataset tells an engaging business story that aligns with GE HealthCare's focus area without requiring a hard-to-source, proprietary clinical telemetry dataset.
- **Trade-offs**: Some relationships (like rotational torque) require creative interpretation for linear medical devices (like ventilators), which we justify as blower fan load.

## 3. Machine Learning Simplification
- **Decision**: Primary focus on **Logistic Regression** and **Random Forest**, with **XGBoost** as a secondary comparison benchmark. LightGBM was excluded.
- **Rationale**: In clinical operations, model interpretability is just as critical as raw prediction accuracy. Logistic Regression provides odds ratios showing how risk increases per degree Celsius or Nm. Random Forest handles non-linear boundaries (e.g., interaction of high hours and speed) while remaining inspectable via feature and permutation importance. Excluding LightGBM reduces codebase bloat and dependencies.
- **Trade-offs**: XGBoost or LightGBM could theoretically yield an extra 0.5% in ROC-AUC, but lose visual clarity and simple explainability.

## 4. Synthetic Timestamp Simulation
- **Decision**: Append continuous hourly timestamps starting from `2026-01-01 00:00:00` for all 10,000 observations.
- **Rationale**: Demonstrates time-series capabilities (rolling averages, anomaly detection, resampling) required of a junior data analyst. The original dataset has no time column, so creating this synthetic date series enables demonstrate-worthy rolling means and forecasting models.
- **Trade-offs**: The simulated time sequence assumes constant hourly intervals between rows, which may not reflect real clinical usage patterns (where devices turn on/off). We explicitly document this in reports and the UI to avoid misleading stakeholders.

## 5. Failure Risk Index Formulation
- **Decision**: Establish a linear heuristic formula: $0.3 \times \text{Temp Stress} + 0.3 \times \text{Mechanical Stress} + 0.4 \times \text{Wear Stress}$.
- **Rationale**: Provides an intuitive KPI that synthesizes multiple variables into a single score. The weights represent a clinical engineer's rule-of-thumb based on failure modes.
- **Trade-offs**: These weights are **not clinically validated** or certified. They are purely heuristic assumptions for analytics demonstrations. We address this limitation by validating the feature's correlation with the true failure targets.
