# 🏭 Manufacturing Analytics Platform

> An end-to-end industrial analytics platform designed to monitor machine health, analyze operational performance, and support predictive maintenance decisions using Python, SQL, Power BI, and Machine Learning.

---

## 📌 Project Overview

Unexpected machine failures in manufacturing environments lead to production delays, increased maintenance costs, and reduced operational efficiency.

As part of a simulated **Project Internship**, this project aims to transform raw machine sensor data into actionable business insights through data analytics, visualization, and predictive modeling.

The platform follows a complete analytics workflow—from understanding and preparing the data to developing executive dashboards and predictive maintenance models.

---

## 🎯 Business Problem

Manufacturing plants generate large volumes of sensor data from production machines. While failures are recorded, operations teams often lack visibility into:

- Which machines are most likely to fail
- The operational conditions leading to failures
- How machine health changes over time
- Key maintenance indicators
- Actionable insights for preventive maintenance

The objective of this project is to develop an analytics solution that enables engineers and decision-makers to monitor equipment health and reduce unplanned downtime.

---

## 🎯 Project Objectives

- Understand and validate manufacturing sensor data
- Perform exploratory data analysis (EDA)
- Engineer meaningful operational features
- Identify patterns associated with machine failures
- Design business KPIs for manufacturing operations
- Build interactive dashboards for decision-makers
- Develop a predictive maintenance model
- Present insights through professional documentation

---

## 📂 Dataset

**Dataset:** AI4I 2020 Predictive Maintenance Dataset

The dataset contains **10,000 manufacturing records** collected from a simulated milling machine.

### Features

| Category | Variables |
|----------|-----------|
| Product Information | UID, Product ID, Product Type |
| Environmental Data | Air Temperature, Process Temperature |
| Machine Operation | Rotational Speed, Torque, Tool Wear |
| Failure Information | Machine Failure, TWF, HDF, PWF, OSF, RNF |

---

## 🛠️ Technology Stack

### Programming

- Python

### Libraries

- Pandas
- NumPy
- Matplotlib
- Plotly
- Scikit-learn

### Data Storage

- SQL

### Visualization

- Power BI

### Version Control

- Git
- GitHub

---

# 📁 Project Structure

```text
manufacturing-analytics-platform/

├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_exploratory_data_analysis.ipynb
│   ├── 04_feature_engineering.ipynb
│   └── 05_predictive_maintenance.ipynb
│
├── src/
│
├── sql/
│
├── dashboard/
│
├── reports/
│
├── images/
│
├── README.md
│
└── requirements.txt
```

---

# 📊 Project Workflow

```
Business Problem
        │
        ▼
Data Collection
        │
        ▼
Data Understanding
        │
        ▼
Data Cleaning
        │
        ▼
Exploratory Data Analysis
        │
        ▼
Feature Engineering
        │
        ▼
SQL Analytics
        │
        ▼
Power BI Dashboard
        │
        ▼
Machine Learning
        │
        ▼
Business Insights & Recommendations
```

---

# 📈 Key Performance Indicators (KPIs)

The platform focuses on operational and maintenance KPIs such as:

- Machine Failure Rate
- Average Tool Wear
- Average Torque
- Average Rotational Speed
- Average Operating Temperature
- Failure Distribution
- Failure by Product Type
- Failure by Failure Mode
- Machine Health Score (Derived)
- Risk Score (Derived)

---

# 📊 Dashboard Modules

### Executive Dashboard

- Overall Machine Health
- Production Overview
- Failure Rate
- Operational KPIs

### Machine Performance Dashboard

- RPM Analysis
- Torque Distribution
- Tool Wear Analysis
- Temperature Monitoring

### Failure Analytics Dashboard

- Failure Trends
- Failure Categories
- Root Cause Analysis

### Predictive Maintenance Dashboard

- Failure Prediction
- High-Risk Machines
- Feature Importance
- Model Performance

---

# 📅 Development Roadmap

- [x] Project Planning
- [x] Repository Setup
- [ ] Data Understanding
- [ ] Data Cleaning
- [ ] Exploratory Data Analysis
- [ ] Feature Engineering
- [ ] SQL Analysis
- [ ] Dashboard Development
- [ ] Machine Learning
- [ ] Business Report
- [ ] Final Documentation

---

# 🎓 Learning Outcomes

This project demonstrates practical experience in:

- Industrial Data Analytics
- Exploratory Data Analysis
- Data Cleaning
- Feature Engineering
- SQL Querying
- Business Intelligence
- Dashboard Design
- Predictive Analytics
- Machine Learning
- Technical Documentation

---

# 🚀 Future Enhancements

- Real-time dashboard integration
- Streaming sensor data
- Automated ETL pipeline
- Cloud deployment
- REST API for predictions
- IoT integration

---

# 📜 Acknowledgements

This project uses the **AI4I 2020 Predictive Maintenance Dataset** developed by **Stephan Matzka**.

Reference:

S. Matzka, *Explainable Artificial Intelligence for Predictive Maintenance Applications*, 2020 Third International Conference on Artificial Intelligence for Industries (AI4I), pp. 69–74.

---

## 👨‍💻 Author

Developed as a portfolio project to simulate the responsibilities of a **Project Intern – Manufacturing Data Analytics**, demonstrating an end-to-end analytics workflow from raw industrial data to actionable business insights.
