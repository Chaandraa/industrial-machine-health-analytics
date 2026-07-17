# Power BI Dashboard Design Guide - Smart ICU Equipment Monitoring

This document serves as a blueprint for implementing the executive dashboard in Microsoft Power BI, detailing table structures, color palettes, visual hierarchies, and DAX measures.

---

## 1. Data Model and Architecture

The report operates on a single-table star schema model directly connected to our SQLite table `icu_equipment`.

* **Primary Table**: `icu_equipment`
* **Data Refresh Strategy**: Incremental daily refresh based on the `Timestamp` column.

---

## 2. Visual Palette & Brand Identity

To fit a premium clinical software aesthetic, use the following hex codes for visual properties:

| Visual Element | Hex Code | Visual Application |
| :--- | :--- | :--- |
| **Deep Slate** | `#0B4F6C` | Titles, headers, primary KPI cards, and trend line charts. |
| **Electric Teal** | `#01BAEF` | Safe/healthy metrics, secondary bars, and low-risk groupings. |
| **Warning Coral** | `#FF5964` | Failures, alarm indicators, high-risk assets, and alert zones. |
| **Soft Gray** | `#FBFBFF` | Report background and visual border strokes. |
| **Slate Gray** | `#607D8B` | Gridlines, secondary axis titles, and label texts. |

---

## 3. DAX Calculations (Measures)

Implement the following DAX measures in the Power BI model:

### A. Total Assets
```dax
Total Assets = COUNT(icu_equipment[Product_ID])
```

### B. Device Outages (Failures)
```dax
Device Outages = CALCULATE(COUNT(icu_equipment[Product_ID]), icu_equipment[Device_Failure] = 1)
```

### C. Outage Rate %
```dax
Outage Rate % = DIVIDE([Device Outages], [Total Assets], 0)
```
*Format: Percentage (`0.00%`)*

### D. Average Health Score
```dax
Average Health Score = AVERAGE(icu_equipment[Health_Score])
```
*Format: Decimal (`0.0`)*

### E. Prioritized High Risk Assets
```dax
High Risk Assets = CALCULATE(COUNT(icu_equipment[Product_ID]), icu_equipment[Maintenance_Risk] = "High")
```
*Format: Whole Number*

### F. Average Operating Hours
```dax
Avg Operating Hours = AVERAGE(icu_equipment[Operating_Hours])
```
*Format: Decimal (`0.0`)*

---

## 4. Visual Layout Grid

Arrange visual components in a $4 \times 3$ grid structure to establish clean visual hierarchies:

```
+-----------------------------------------------------------------------------+
|                                  HEADER ZONE                                |
|  [GE HealthCare Logo]    ICU Telemetry Predictive Monitoring Dashboard      |
+-------------------+-------------------+-------------------+-----------------+
|     TOTAL ASSETS  |   OUTAGE RATE %   | AVG HEALTH SCORE  | HIGH RISK COUNT |
|      10,000       |       3.39%       |       94.6        |       423       |
+-------------------+-------------------+-------------------+-----------------+
| [SLICERS PANEL]   | [OPERATING ENVELOPE CHART]                              |
| - Equip Type      | Scatter plot of Temp Diff vs Motor Load                 |
| - Risk Class      | Failed assets highlight in Coral Red.                   |
| - Failures        |                                                         |
+-------------------+---------------------------------------------------------+
| [FAILURE MODES]   | [PREVENTIVE MAINTENANCE CHECKLIST (BQ3)]                |
| Treemap showing   | Table of Product ID, Category, Health Score, Wear       |
| HDF, OSF, PWF...  | Sorted by Health Score ascending.                       |
+-------------------+---------------------------------------------------------+
```

### Visual Specifications
1. **KPI Cards (Row 1)**: Simple, large font values ($40\text{pt}$ bold) with secondary label texts underneath. Apply Warning Coral borders to the "High Risk Count" card if the value exceeds 50.
2. **Slicer Panel (Column 1)**: Dropdown controls for `Equipment_Category`, `Maintenance_Risk`, and `Device_Failure`. Enable multi-select with search options.
3. **Scatter Plot (Row 2, Column 2-4)**: X-axis: `Motor_Load_Nm`, Y-axis: `Temp_Diff`. Color mapped to `Device_Failure` (Healthy = Electric Teal, Failed = Warning Coral). Helps visually map the critical failure envelope.
4. **Treemap (Row 3, Column 1)**: Values represent the sum of specific failure modes (`Failure_Overheating`, `Failure_Component_Wear`, etc.). Shows the division of breakdown causes.
5. **Checklist Grid (Row 3, Column 2-4)**: Multi-column table filtered to `Maintenance_Risk = "High"` and sorted ascending by `Health_Score` (lowest health at the top). Enables technicians to copy Product IDs directly for daily dispatch.
