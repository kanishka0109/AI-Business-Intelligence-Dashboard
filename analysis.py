"""
analysis.py - KPI computation, anomaly detection, and trend analysis.

This is the brain of the dashboard. It takes the cleaned data and computes:
  - Summary statistics per column
  - Trend direction via linear regression
  - Anomaly flags using IQR method
  - Correlation matrix
  - Category-wise aggregations

You'll learn:
  - Statistical analysis with pandas and numpy
  - Linear regression with scipy
  - How to structure computed metrics for display
"""

import pandas as pd
import numpy as np
from scipy import stats


def compute_numeric_kpis(df):
    """Calculate mean, median, std, min/max for all numeric columns."""
    num_df = df.select_dtypes(include='number')

    means = num_df.mean()
    medians = num_df.median()
    stds = num_df.std()
    mins = num_df.min()
    maxs = num_df.max()

    result = {
        'mean': means,
        'median': medians,
        'std': stds,
        'min': mins,
        'max': maxs,
    }
    return pd.DataFrame(result)


def detect_trends(df, date_col, numeric_col):
    """Use linear regression to determine trend direction and strength."""
    sorted_df = df.sort_values(date_col)
    x = np.arange(len(sorted_df))
    y = sorted_df[numeric_col]
    result = stats.linregress(x, y)
    if result.slope > 0:
        direction = "up"
    elif result.slope < 0:
        direction = "down"
    else:
        direction = "flat"
    return {"slope": result.slope, "direction": direction, "p_value": result.pvalue}


def detect_anomalies(df):
    """Flag outliers in numeric columns using the IQR method."""
    num_df = df.select_dtypes(include='number')
    Q1 = num_df.quantile(0.25)
    Q3 = num_df.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    anomaly_flag = (num_df < lower) | (num_df > upper)
    return {"flags": anomaly_flag, "count": anomaly_flag.sum()}


def compute_correlation_matrix(df):
    """Return correlation matrix for all numeric columns."""
    num_df = df.select_dtypes(include='number')
    corr_matrix = num_df.corr()
    return corr_matrix


def compute_category_stats(df):
    """For categorical columns: unique count, top categories, concentration ratio."""
    cat_df = df.select_dtypes(exclude='number')
    result = {}
    for col in cat_df.columns:
        unique = cat_df[col].nunique()
        top = cat_df[col].mode()[0]
        concentration = cat_df[col].value_counts().iloc[0] / len(cat_df[col])
        result[col] = {
            "unique": unique,
            "top": top,
            "concentration": concentration
        }
    return result
