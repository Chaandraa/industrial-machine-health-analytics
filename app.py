"""Streamlit application for the Smart ICU Equipment monitoring platform.

Presents the operational analytics dashboards, predictive diagnosis tools,
time-series forecasts, and business insights reports in a clean, user-friendly layout.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import json
import os
from datetime import datetime, timedelta
from src.config import (
    PROCESSED_DATA_PATH,
    MODELS_DIR,
    DB_PATH,
    COLUMN_MAPPING
)
from src.utils import run_query
from src.preprocessing import run_data_quality_report
from src.feature_engineering import (
    calculate_temperature_difference,
    calculate_utilization_percentage,
    calculate_failure_risk_index,
    categorize_maintenance_risk
)

# Set page configuration
st.set_page_color = "light"
st.set_page_config(
    page_title="Smart ICU Equipment Analytics Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GE HealthCare Brand-Inspired Palette
CLINICAL_COLORS = {
    "primary": "#0B4F6C",      # Deep Slate Blue
    "secondary": "#01BAEF",    # Electric Teal
    "accent": "#FF5964",       # Warning Coral/Red
    "healthy": "#2EC4B6",      # Clinical Teal-Green
    "failed": "#E71D36",       # Alert Red
    "background": "#FBFBFF"
}

# ==============================================================================
# Helper Functions
# ==============================================================================
@st.cache_resource
def load_models_and_metadata():
    """Loads trained ML models and serialized evaluation metadata."""
    try:
        lr = joblib.load(MODELS_DIR / "logisticregression_v1.joblib")
        rf = joblib.load(MODELS_DIR / "randomforest_v1.joblib")
        
        metadata_path = MODELS_DIR / "model_metadata.json"
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                meta = json.load(f)
        else:
            meta = {}
            
        return lr, rf, meta
    except Exception as e:
        st.error(f"Error loading models or metadata: {e}")
        return None, None, {}

@st.cache_data
def load_processed_data():
    """Loads processed telemetry dataset from CSV."""
    if os.path.exists(PROCESSED_DATA_PATH):
        df = pd.read_csv(PROCESSED_DATA_PATH)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        return df
    else:
        st.error(f"Processed dataset not found at {PROCESSED_DATA_PATH}. Run pipeline first.")
        return pd.DataFrame()

# Load assets
lr_model, rf_model, model_meta = load_models_and_metadata()
df_processed = load_processed_data()

# ==============================================================================
# Sidebar Navigation
# ==============================================================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e1/GE_Healthcare_logo.svg", width=120)
st.sidebar.title("ICU Monitoring Hub")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation Menu",
    [
        "🏠 Executive Summary",
        "📊 Operational Analytics",
        "🔮 Telemetry Diagnostics",
        "📈 Time-Series & Forecasts"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Platform Status**:  
    🟢 Online (SQL active)  
    **Environment**:  
    `Developer Preview (v1)`
    """
)

# ==============================================================================
# View 1: Executive Summary
# ==============================================================================
if page == "🏠 Executive Summary":
    st.title("🏥 Smart ICU Equipment Monitoring & Analytics Platform")
    st.subheader("A Data Engineering + Predictive Analytics Platform for GE HealthCare Systems")
    
    st.markdown("---")
    
    # Grid KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Assets Monitored", value=f"{len(df_processed):,}")
    with col2:
        outages = int(df_processed["Device_Failure"].sum())
        outage_rate = (outages / len(df_processed)) * 100
        st.metric(label="Active Outages", value=outages, delta=f"{outage_rate:.2f}% Rate", delta_color="inverse")
    with col3:
        avg_health = df_processed["Health_Score"].mean()
        st.metric(label="Average Health Score", value=f"{avg_health:.1f}%")
    with col4:
        high_risk = len(df_processed[df_processed["Maintenance_Risk"] == "High"])
        st.metric(label="High-Risk Warnings", value=high_risk, delta="Action Required", delta_color="inverse")
        
    st.markdown("---")
    
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.markdown(
            """
            ### Business Objectives
            ICU equipment reliability is critical for hospital performance and patient survival. Unexpected breakdown of MRI machines, CT Scanners, or Ventilators results in thousands of dollars in cancelled clinical procedures and emergency maintenance surcharges.
            
            This platform acts as an automated monitoring solution, capturing raw sensor streams and:
            1. **Executing Data Auditing**: Ensuring data schema completeness and range validity.
            2. **Translating Telemetry**: Reframing industrial readings into clean clinical telemetry.
            3. **Calculating Asset Health**: Synthesizing motor load, thermal stress, and operating wear.
            4. **Predicting Failures**: Classifying device risks via trained Machine Learning models.
            5. **Triaging Dispatches**: Supplying high-risk assets lists directly to technician workflows.
            """
        )
    with col_right:
        st.markdown(
            """
            ### Clinical Reframing Model
            - **Ventilator** (Type L): High frequency, routine wear metrics.
            - **CT Scanner** (Type M): Medium frequency, moderate thermal stresses.
            - **MRI Machine** (Type H): Low frequency, high cooling criticality.
            - **Operating Hours** (Original Tool Wear): Run time since last service.
            - **Motor Load** (Original Torque): Rotational mechanical stress.
            - **Temperature Diff**: Dissipation gradient ($T_{\text{internal}} - T_{\text{ambient}}$).
            """
        )
        
    st.markdown("---")
    st.markdown("### System Integration & ETL Architecture")
    st.markdown(
        """
        ```mermaid
        graph LR
            A[Raw Sensor CSV] --> B[Validation & Quality Report]
            B --> C[ETL Transformation & Feature Engineering]
            C --> D[SQLite Database: sql/healthcare_maintenance.db]
            D --> E[Interactive Dashboards & SQL Reporting]
            C --> F[Random Forest Classifiers]
            F --> G[Predictive Diagnostic Tool]
        ```
        *This Mermaid flow diagram illustrates the data ingestion and model inference pipeline.*
        """
    )

# ==============================================================================
# View 2: Operational Analytics (Power BI Dashboard Mockup)
# ==============================================================================
elif page == "📊 Operational Analytics":
    st.title("📊 Operational Analytics Dashboard")
    st.subheader("Interactive KPI metrics and visual reports mapping to Business Analytics Questions")
    
    st.markdown("---")
    
    # Sidebar filter inside this page for interactive slicing
    selected_category = st.selectbox(
        "Filter by Equipment Category",
        ["All Categories", "Ventilator", "CT Scanner", "MRI Machine"]
    )
    
    # Filter dataset
    if selected_category == "All Categories":
        df_filtered = df_processed
    else:
        df_filtered = df_processed[df_processed["Equipment_Category"] == selected_category]
        
    # KPIs for filtered set
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Asset Count", f"{len(df_filtered):,}")
    with c2:
        outages_f = int(df_filtered["Device_Failure"].sum())
        outage_rate_f = (outages_f / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0.0
        st.metric("Outages", outages_f, delta=f"{outage_rate_f:.2f}% Outage Rate", delta_color="inverse")
    with c3:
        avg_health_f = df_filtered["Health_Score"].mean() if len(df_filtered) > 0 else 100.0
        st.metric("Avg Health Score", f"{avg_health_f:.1f}%")
    with c4:
        high_risk_f = len(df_filtered[df_filtered["Maintenance_Risk"] == "High"])
        st.metric("High-Risk Count", high_risk_f)
        
    st.markdown("---")
    
    # Question 1 & 2
    row1_left, row1_right = st.columns(2)
    with row1_left:
        st.markdown("#### Equipment Category Outage Distribution (BQ1)")
        # Calculate rates
        grouped = df_processed.groupby("Equipment_Category").agg(
            Total_Assets=("Device_Failure", "count"),
            Failures=("Device_Failure", "sum")
        ).reset_index()
        grouped["Outage_Rate_Pct"] = np.round((grouped["Failures"] / grouped["Total_Assets"]) * 100, 2)
        
        fig_bq1 = go.Figure()
        fig_bq1.add_trace(go.Bar(
            x=grouped["Equipment_Category"], y=grouped["Failures"],
            name="Failures (units)", marker_color=CLINICAL_COLORS["accent"]
        ))
        fig_bq1.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=40, b=40), height=300)
        st.plotly_chart(fig_bq1, use_container_width=True)
        st.caption("Which equipment type fails most frequently? Ventilators show the highest raw count due to their volume.")
        
    with row1_right:
        st.markdown("#### Operating Temperature vs Load Envelope (BQ2)")
        df_plot = df_filtered.copy()
        df_plot["Status"] = df_plot["Device_Failure"].map({0: "Healthy", 1: "Failed"})
        fig_bq2 = px.scatter(
            df_plot, x="Motor_Load_Nm", y="Temp_Diff", color="Status",
            color_discrete_map={"Healthy": CLINICAL_COLORS["healthy"], "Failed": CLINICAL_COLORS["failed"]},
            labels={"Motor_Load_Nm": "Motor Load (Nm)", "Temp_Diff": "Temp Diff (°C)"}
        )
        fig_bq2.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=40, b=40), height=300)
        st.plotly_chart(fig_bq2, use_container_width=True)
        st.caption("Failed assets cluster at Temp Differences > 8.5°C and Motor Loads > 55 Nm.")
        
    st.markdown("---")
    
    # Question 3 & 4
    row2_left, row2_right = st.columns([1, 2])
    with row2_left:
        st.markdown("#### Common Outage Modes Breakdown")
        fail_modes = {
            "Wear": int(df_filtered["Failure_Component_Wear"].sum()),
            "Overheat": int(df_filtered["Failure_Overheating"].sum()),
            "Power Supply": int(df_filtered["Failure_Power_Supply"].sum()),
            "Overload": int(df_filtered["Failure_Overload"].sum()),
            "Random": int(df_filtered["Failure_Random_Hardware"].sum())
        }
        df_fail_modes = pd.DataFrame(list(fail_modes.items()), columns=["Failure Mode", "Count"])
        fig_pie = px.pie(
            df_fail_modes, values="Count", names="Failure Mode",
            color_discrete_sequence=[CLINICAL_COLORS["accent"], CLINICAL_COLORS["primary"], CLINICAL_COLORS["secondary"], "#e5c158", "#9a9a9a"]
        )
        fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=280)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with row2_right:
        st.markdown("#### Prioritized Maintenance Work Order List (BQ3)")
        # SQLite query lookup
        priority_list = df_filtered[df_filtered["Maintenance_Risk"] == "High"].sort_values(
            by="Health_Score", ascending=True
        )[["Product_ID", "Equipment_Category", "Health_Score", "Operating_Hours", "Motor_Load_Nm", "Temp_Diff"]].head(10)
        
        st.dataframe(priority_list, use_container_width=True)
        st.caption("Service priorities are triaged by Health Score. These Product IDs should receive preventative maintenance immediately.")

# ==============================================================================
# View 3: Predictive Diagnostics
# ==============================================================================
elif page == "🔮 Telemetry Diagnostics":
    st.title("🔮 Telemetry Diagnostics & Risk Predictor")
    st.subheader("Evaluate live device parameters using Random Forest and Logistic Regression models")
    
    st.markdown("---")
    
    # Model evaluation metrics info
    with st.expander("Model Performance Metrics & Version Details"):
        if model_meta and "RandomForest" in model_meta:
            rf_metrics = model_meta["RandomForest"]["metrics"]
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            col_m1.metric("Production Model", "Random Forest")
            col_m2.metric("Recall (Sensitivity)", f"{rf_metrics['recall']*100:.2f}%")
            col_m3.metric("Precision", f"{rf_metrics['precision']*100:.2f}%")
            col_m4.metric("F1-Score", f"{rf_metrics['f1_score']*100:.2f}%")
            col_m5.metric("ROC-AUC", f"{rf_metrics['roc_auc']*100:.2f}%")
            st.info("Random Forest is deployed as our primary model because it prioritizes Recall, minimizing missed failures in clinical settings.")
        else:
            st.warning("Model metadata details unavailable.")
            
    st.markdown("### Diagnose Single Equipment Unit")
    
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        eq_type = st.selectbox("Equipment Type", ["Ventilator", "CT Scanner", "MRI Machine"])
        operating_hours = st.slider("Operating Hours Since Maintenance", 0, 300, 120)
    with col_in2:
        ambient_temp = st.number_input("Ambient Room Temperature (°C)", 15.0, 35.0, 22.0, step=0.5)
        internal_temp = st.number_input("Internal Device Temperature (°C)", 25.0, 50.0, 31.0, step=0.5)
    with col_in3:
        fan_speed = st.number_input("Cooling Fan Speed (RPM)", 1000, 3000, 1500, step=50)
        motor_load = st.number_input("Motor Load (Nm)", 0.0, 100.0, 40.0, step=1.0)
        
    if st.button("Run Diagnostic Evaluation"):
        # Process inputs
        temp_diff = internal_temp - ambient_temp
        
        # Calculate Utilization Pct
        power_proxy = fan_speed * motor_load
        util_pct = np.minimum(100.0, (power_proxy / 60000.0) * 100.0)
        
        # Calculate Failure Risk Index
        term_temp = temp_diff / 15.0
        term_load = motor_load / 80.0
        term_wear = operating_hours / 250.0
        risk_index = np.clip((0.3 * term_temp) + (0.3 * term_load) + (0.4 * term_wear), 0.0, 1.0)
        
        # Calculate Health Score and Risk Category
        health_score = np.round(100.0 - (risk_index * 100.0), 2)
        
        conditions = [health_score >= 80, (health_score >= 60) & (health_score < 80), health_score < 60]
        choices = ["Low", "Medium", "High"]
        risk_cat = np.select(conditions, choices, default="Low")
        
        # ML Inference Matrix
        input_data = pd.DataFrame([{
            "Ambient_Room_Temp_C": ambient_temp,
            "Internal_Device_Temp_C": internal_temp,
            "Cooling_Fan_Speed_RPM": fan_speed,
            "Motor_Load_Nm": motor_load,
            "Operating_Hours": operating_hours,
            "Temp_Diff": temp_diff,
            "Utilization_Pct": util_pct,
            "Failure_Risk_Index": risk_index
        }])
        
        # Predict probability
        failure_prob_rf = rf_model.predict_proba(input_data)[0][1]
        failure_prob_lr = lr_model.predict_proba(input_data)[0][1]
        
        st.markdown("---")
        st.markdown("### Diagnostic Report")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Engineered Health Score", f"{health_score:.1f}%")
        with col_r2:
            st.metric("Maintenance Risk Level", str(risk_cat))
        with col_r3:
            st.metric("Predicted Failure Probability (RF)", f"{failure_prob_rf * 100:.1f}%")
            
        # Recommendations
        st.markdown("#### Clinical Action Plan")
        if risk_cat == "High" or failure_prob_rf > 0.5:
            st.error("🚨 **CRITICAL RISK FLAG**: Device is operating in a failure state or shows severe telemetry degradation. Schedule immediate technician dispatch.")
            if temp_diff > 8.5:
                st.markdown("- *Reasoning*: High temperature difference indicates overheating danger. Inspect blower/cooling fan.")
            if motor_load > 55.0:
                st.markdown("- *Reasoning*: Excessive torque load detected. Reduce operational load limits.")
            if operating_hours > 180:
                st.markdown("- *Reasoning*: Run hours exceed safety margins. Schedule component replacement wear service.")
        elif risk_cat == "Medium":
            st.warning("⚠️ **WARNING**: Device shows early indicators of mechanical or thermal degradation. Schedule service check within the next 48 hours.")
        else:
            st.success("💚 **NORMAL OPERATIONS**: Device telemetry is well within normal clinical and mechanical limits. Continue routine monitoring.")
            
        # Download report
        report_text = f"""==================================================
GE HEALTHCARE SMART ICU EQUIPMENT DIAGNOSTIC REPORT
==================================================
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Asset Category: {eq_type}
--------------------------------------------------
Telemetry Parameters:
- Ambient Room Temp: {ambient_temp} C
- Internal Device Temp: {internal_temp} C
- Temperature Diff: {temp_diff:.2f} C
- Cooling Fan Speed: {fan_speed} RPM
- Motor Load: {motor_load} Nm
- Operating Hours: {operating_hours} Hours
--------------------------------------------------
Calculated Diagnostics:
- Power Utilization: {util_pct:.1f}%
- Failure Risk Index: {risk_index:.3f}
- Engineered Health Score: {health_score:.1f}%
- Maintenance Risk Level: {risk_cat}
--------------------------------------------------
ML Outage Prognosis:
- Random Forest Prob: {failure_prob_rf * 100:.2f}%
- Logistic Regression Prob: {failure_prob_lr * 100:.2f}%
=================================================="""
        
        st.download_button(
            label="Download Diagnostic Report File",
            data=report_text,
            file_name=f"diagnostic_report_{eq_type}.txt",
            mime="text/plain"
        )

# ==============================================================================
# View 4: Time-Series & Forecasting
# ==============================================================================
elif page == "📈 Time-Series & Forecasts":
    st.title("📈 Simulated Time-Series Analysis")
    st.subheader("Demonstrating temporal analytics, rolling statistics, and trend forecasts")
    st.info("DISCLAIMER: The time axis and chronological logs are synthetically generated for demonstration purposes and do not represent historical clinical hospital databases.")
    
    st.markdown("---")
    
    # Aggregate to daily levels
    df_ts = df_processed.copy()
    df_ts = df_ts.set_index("Timestamp")
    
    df_daily = df_ts.resample("D").agg({
        "Ambient_Room_Temp_C": "mean",
        "Internal_Device_Temp_C": "mean",
        "Temp_Diff": "mean",
        "Device_Failure": "sum",
        "Health_Score": "mean"
    }).reset_index()
    
    # 7-day rolling statistics
    df_daily["Rolling_Avg_Temp_Diff"] = df_daily["Temp_Diff"].rolling(window=7, min_periods=1).mean()
    df_daily["Rolling_Std_Temp_Diff"] = df_daily["Temp_Diff"].rolling(window=7, min_periods=1).std()
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("#### Daily Average Temperature Difference (7-Day Rolling)")
        fig_diff = go.Figure()
        fig_diff.add_trace(go.Scatter(
            x=df_daily["Timestamp"], y=df_daily["Temp_Diff"],
            name="Daily Mean Temp Diff", line=dict(color=CLINICAL_COLORS["secondary"], width=1)
        ))
        fig_diff.add_trace(go.Scatter(
            x=df_daily["Timestamp"], y=df_daily["Rolling_Avg_Temp_Diff"],
            name="7-Day Rolling Mean", line=dict(color=CLINICAL_COLORS["primary"], width=2)
        ))
        fig_diff.update_layout(template="plotly_white", height=320, margin=dict(l=40, r=40, t=20, b=40))
        st.plotly_chart(fig_diff, use_container_width=True)
        
    with col_t2:
        st.markdown("#### Weekly Asset Outages (Daily Sums)")
        fig_out = go.Figure()
        fig_out.add_trace(go.Bar(
            x=df_daily["Timestamp"], y=df_daily["Device_Failure"],
            name="Daily Failures", marker_color=CLINICAL_COLORS["accent"]
        ))
        fig_out.update_layout(template="plotly_white", height=320, margin=dict(l=40, r=40, t=20, b=40))
        st.plotly_chart(fig_out, use_container_width=True)
        
    st.markdown("---")
    st.markdown("#### Simple Wear-out & Risk Forecasting")
    st.markdown(
        """
        By tracking the slope of cumulative wear hours and rolling temperature stress, clinical planners can forecast when an active machine is likely to hit the critical threshold of $180\text{ hours}$ or cross into the High-Risk category.
        """
    )
    
    # Pick a specific machine to model forecast
    m_id = st.selectbox("Select Asset Serial Number to Model", df_processed["Product_ID"].unique()[:10])
    
    m_data = df_processed[df_processed["Product_ID"] == m_id].sort_values("Timestamp")
    
    # Forecast wear hours linearly
    current_wear = m_data["Operating_Hours"].iloc[-1]
    
    forecast_days = 30
    forecast_dates = [m_data["Timestamp"].iloc[-1] + timedelta(hours=i) for i in range(1, forecast_days + 1)]
    # Assume 1.5 operating hours accumulated per hour of use
    forecast_wear = [current_wear + (1.2 * i) for i in range(1, forecast_days + 1)]
    
    fig_f = go.Figure()
    fig_f.add_trace(go.Scatter(
        x=m_data["Timestamp"], y=m_data["Operating_Hours"],
        name="Historic Operating Hours", line=dict(color=CLINICAL_COLORS["primary"], width=2)
    ))
    fig_f.add_trace(go.Scatter(
        x=forecast_dates, y=forecast_wear,
        name="Forecasted Wear Hours", line=dict(color=CLINICAL_COLORS["accent"], width=2, dash="dash")
    ))
    fig_f.add_hline(y=180, line_dash="dot", line_color="orange", annotation_text="PM Advisory Limit (180h)")
    fig_f.add_hline(y=200, line_dash="dot", line_color="red", annotation_text="Critical Limit (200h)")
    
    fig_f.update_layout(
        template="plotly_white",
        height=320,
        title=f"<b>Wear Hour Trajectory Forecast for Asset {m_id}</b>",
        xaxis_title="Time Axis",
        yaxis_title="Operating Hours",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig_f, use_container_width=True)
    
    # Project outage date
    days_to_alert = (180 - current_wear) / 1.2 if current_wear < 180 else 0
    if days_to_alert > 0:
        alert_date = datetime.now() + timedelta(days=days_to_alert)
        st.success(f"Asset is currently healthy. At present utilization rate, it is projected to cross the 180-hour PM limit in **{days_to_alert:.1f} hours** (approx. **{alert_date.strftime('%Y-%m-%d')}**).")
    else:
        st.warning(f"Asset has already crossed the 180-hour threshold ({current_wear} hours). Dispatch technician immediately for preventative component service.")
