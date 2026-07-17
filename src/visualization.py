"""Shared visualization utilities for standard reporting.

Provides charting functions mapping directly to the Business Analytics Questions:
- BQ1: Which equipment type fails most frequently?
- BQ2: Which operating conditions lead to failures?
- BQ4: What operating-hour threshold significantly increases failure risk?
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, Tuple

# GE HealthCare Brand-Inspired Palette (Slate Gray, Teal Blue, Coral Warning)
CLINICAL_COLORS = {
    "primary": "#0B4F6C",      # Deep Slate Blue
    "secondary": "#01BAEF",    # Electric Teal
    "accent": "#FF5964",       # Warning Coral/Red
    "healthy": "#2EC4B6",      # Clinical Teal-Green
    "failed": "#E71D36",       # Alert Red
    "background": "#FBFBFF",   # Soft Gray-White
    "dark_grid": "#E0E0E0"
}

def set_style() -> None:
    """Sets standard Matplotlib and Seaborn plotting styles."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.facecolor"] = CLINICAL_COLORS["background"]
    plt.rcParams["axes.facecolor"] = CLINICAL_COLORS["background"]
    plt.rcParams["axes.edgecolor"] = CLINICAL_COLORS["dark_grid"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 10

def plot_correlation_heatmap(df: pd.DataFrame, columns: list, title: str = "Telemetry Correlation Matrix") -> plt.Figure:
    """Plots a Seaborn correlation heatmap for selected numeric variables.

    Args:
        df: Input DataFrame.
        columns: List of numeric columns to evaluate.
        title: Title of the chart.

    Returns:
        plt.Figure: The generated figure.
    """
    set_style()
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Calculate matrix
    corr = df[columns].corr()
    
    # Generate mask for upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    # Draw heatmap
    sns.heatmap(
        corr,
        mask=mask,
        cmap=sns.diverging_palette(220, 10, as_cmap=True),
        vmax=1.0,
        vmin=-1.0,
        center=0,
        square=True,
        linewidths=.5,
        cbar_kws={"shrink": .8},
        annot=True,
        fmt=".2f",
        ax=ax
    )
    ax.set_title(title, fontsize=12, fontweight="bold", pad=15)
    plt.tight_layout()
    return fig

def plot_failures_by_equipment(df: pd.DataFrame) -> go.Figure:
    """Creates a Plotly bar chart showing failure counts and failure rates by Equipment Category.

    Answers BQ1: Which equipment type fails most frequently?

    Args:
        df: Input processed DataFrame.

    Returns:
        go.Figure: Plotly bar chart figure.
    """
    # Group by equipment
    grouped = df.groupby("Equipment_Category").agg(
        Total_Assets=("Device_Failure", "count"),
        Failures=("Device_Failure", "sum")
    ).reset_index()
    
    grouped["Failure_Rate_Pct"] = np.round((grouped["Failures"] / grouped["Total_Assets"]) * 100, 2)
    
    fig = go.Figure()
    
    # Bar for Failures
    fig.add_trace(go.Bar(
        x=grouped["Equipment_Category"],
        y=grouped["Failures"],
        name="Failure Count",
        marker_color=CLINICAL_COLORS["accent"],
        yaxis="y1"
    ))
    
    # Line for Failure Rate
    fig.add_trace(go.Scatter(
        x=grouped["Equipment_Category"],
        y=grouped["Failure_Rate_Pct"],
        name="Failure Rate (%)",
        marker_color=CLINICAL_COLORS["primary"],
        yaxis="y2",
        mode="lines+markers"
    ))
    
    # Layout configuration
    fig.update_layout(
        title={
            "text": "<b>Equipment Category Failure Profile (BQ1)</b>",
            "y":0.9,
            "x":0.5,
            "xanchor": "center",
            "yanchor": "top"
        },
        xaxis=dict(title="Equipment Category"),
        yaxis=dict(
            title="Failure Count (units)",
            titlefont=dict(color=CLINICAL_COLORS["accent"]),
            tickfont=dict(color=CLINICAL_COLORS["accent"])
        ),
        yaxis2=dict(
            title="Failure Rate (%)",
            titlefont=dict(color=CLINICAL_COLORS["primary"]),
            tickfont=dict(color=CLINICAL_COLORS["primary"]),
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.01, y=0.99),
        template="plotly_white",
        height=400
    )
    return fig

def plot_operating_envelope(df: pd.DataFrame) -> go.Figure:
    """Generates a Plotly scatter plot of Temp_Diff vs Motor_Load_Nm, highlighting failures.

    Answers BQ2: Which operating conditions lead to failures?

    Args:
        df: Input processed DataFrame.

    Returns:
        go.Figure: Plotly scatter figure.
    """
    df_plot = df.copy()
    df_plot["Status"] = df_plot["Device_Failure"].map({0: "Healthy", 1: "Failed"})
    
    fig = px.scatter(
        df_plot,
        x="Motor_Load_Nm",
        y="Temp_Diff",
        color="Status",
        color_discrete_map={"Healthy": CLINICAL_COLORS["healthy"], "Failed": CLINICAL_COLORS["failed"]},
        hover_data=["Product_ID", "Equipment_Category", "Operating_Hours", "Health_Score"],
        labels={"Motor_Load_Nm": "Motor Load (Nm)", "Temp_Diff": "Temperature Difference (°C)"},
        title="<b>Operating Failure Envelope: Temp Difference vs Motor Load (BQ2)</b>"
    )
    
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(title="Motor Load (Nm)"),
        yaxis=dict(title="Temperature Difference (°C)"),
        legend_title_text="Device State",
        height=450
    )
    return fig

def plot_wear_threshold(df: pd.DataFrame) -> plt.Figure:
    """Generates a Seaborn distribution plot showing Operating_Hours for failed vs healthy units.

    Answers BQ4: What operating-hour threshold significantly increases failure risk?

    Args:
        df: Input processed DataFrame.

    Returns:
        plt.Figure: The Matplotlib figure.
    """
    set_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    
    sns.kdeplot(
        data=df[df["Device_Failure"] == 0],
        x="Operating_Hours",
        fill=True,
        label="Healthy Equipment",
        color=CLINICAL_COLORS["healthy"],
        alpha=0.4,
        ax=ax
    )
    
    sns.kdeplot(
        data=df[df["Device_Failure"] == 1],
        x="Operating_Hours",
        fill=True,
        label="Failed Equipment",
        color=CLINICAL_COLORS["failed"],
        alpha=0.6,
        ax=ax
    )
    
    # Draw vertical advisory line at 180 operating hours (the recommendation threshold)
    ax.axvline(180, color=CLINICAL_COLORS["primary"], linestyle="--", linewidth=1.5)
    ax.text(182, 0.003, "Advisory Wear Limit (180 Hours)", color=CLINICAL_COLORS["primary"], fontweight="bold")
    
    ax.set_title("Operating Hours Failure Distribution Analysis (BQ4)", fontsize=12, fontweight="bold", pad=15)
    ax.set_xlabel("Operating Hours Since Maintenance")
    ax.set_ylabel("Density")
    ax.legend(loc="upper left")
    plt.tight_layout()
    return fig
