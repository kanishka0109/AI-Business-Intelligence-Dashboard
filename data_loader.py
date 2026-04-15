"""
data_loader.py - File ingestion, type detection, and auto-cleaning pipeline.

DATA FLOW:
  Upload → load_file() → detect_column_types() → clean_data() → (clean DataFrame + log)

KEY CONCEPTS YOU'LL LEARN:
  - pd.read_csv / pd.read_excel  → loading data into DataFrames
  - pd.to_datetime               → parsing dates from strings
  - df.select_dtypes             → filtering columns by type
  - df.isnull().sum()            → counting missing values
  - IQR method                   → statistical outlier detection
"""

import pandas as pd
import numpy as np
from config import NULL_THRESHOLD, IQR_MULTIPLIER


# ──────────────────────────────────────────────
# STEP 1: Load the uploaded file into a DataFrame
# ──────────────────────────────────────────────

def load_file(uploaded_file):
    """
    Load a CSV or Excel file into a pandas DataFrame.

    HOW IT WORKS:
    - Checks the file extension to decide csv vs excel
    - pd.read_csv() / pd.read_excel() do the heavy lifting
    - Returns the raw DataFrame before any cleaning

    WHY: Pandas DataFrames are the core data structure for tabular data.
    Think of it as a programmable spreadsheet.
    """
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif file_name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file type: {file_name}")

    return df


# ──────────────────────────────────────────────
# STEP 2: Auto-detect what type each column is
# ──────────────────────────────────────────────

def detect_column_types(df):
    """
    Classify each column as: numeric, categorical, datetime, or boolean.

    HOW IT WORKS:
    - First, tries to parse any string column as a date (pd.to_datetime)
    - Then uses pandas dtype checking for numeric/bool
    - Everything else is treated as categorical (text)

    WHY: The rest of the pipeline (KPIs, charts, cleaning) behaves differently
    based on column type. Numeric columns get mean/median, categorical get
    frequency counts, datetime columns enable trend analysis.

    RETURNS: dict like {"numeric": [...], "categorical": [...], "datetime": [...], "boolean": [...]}
    """
    col_types = {
        "numeric": [],
        "categorical": [],
        "datetime": [],
        "boolean": []
    }

    for col in df.columns:
        # Check if it's already a datetime type
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            col_types["datetime"].append(col)
            continue

        # Try to parse as datetime — many dates come in as strings
        # errors="coerce" turns unparseable values into NaT (Not a Time)
        if pd.api.types.is_string_dtype(df[col]):
            try:
                parsed = pd.to_datetime(df[col], format="mixed", dayfirst=False)
                # If more than 50% parsed successfully, it's a date column
                if parsed.notna().sum() / len(parsed) > 0.5:
                    df[col] = parsed
                    col_types["datetime"].append(col)
                    continue
            except (ValueError, TypeError):
                pass

        # Check boolean (must come before numeric since bool is technically numeric)
        if pd.api.types.is_bool_dtype(df[col]):
            col_types["boolean"].append(col)
        # Check numeric
        elif pd.api.types.is_numeric_dtype(df[col]):
            col_types["numeric"].append(col)
        # Everything else is categorical
        else:
            col_types["categorical"].append(col)

    return col_types


# ──────────────────────────────────────────────
# STEP 3: Auto-clean the data
# ──────────────────────────────────────────────

def clean_data(df):
    """
    Run the full auto-cleaning pipeline. Returns (cleaned_df, cleaning_log).

    PIPELINE STEPS:
    1. Drop columns with too many nulls (>50% by default)
    2. Impute remaining missing values (median for numbers, mode for categories)
    3. Remove duplicate rows
    4. Flag statistical outliers using the IQR method

    WHY EACH STEP:
    - High-null columns add noise, not signal — drop them
    - Imputation keeps rows usable instead of dropping them entirely
    - Duplicates skew aggregations (double-counting)
    - Outlier flags don't remove data, they mark it for the user to investigate

    RETURNS: (cleaned DataFrame, list of log messages)
    """
    log = []  # We'll track every action so the user knows what changed
    df = df.copy()  # Never modify the original — always work on a copy

    # --- 3a: Drop high-null columns ---
    # For each column, calculate what fraction of values are null
    null_ratios = df.isnull().sum() / len(df)
    high_null_cols = null_ratios[null_ratios > NULL_THRESHOLD].index.tolist()

    if high_null_cols:
        df = df.drop(columns=high_null_cols)
        log.append(f"Dropped {len(high_null_cols)} column(s) with >{NULL_THRESHOLD*100:.0f}% nulls: {high_null_cols}")

    # --- 3b: Impute missing values ---
    # Numeric columns → fill with median (robust to outliers, unlike mean)
    # Categorical columns → fill with mode (most frequent value)
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            log.append(f"Imputed {missing_count} missing value(s) in '{col}' with median ({median_val:.2f})")

    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in categorical_cols:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            mode_val = df[col].mode()[0]  # mode() returns a Series; [0] gets the top value
            df[col] = df[col].fillna(mode_val)
            log.append(f"Imputed {missing_count} missing value(s) in '{col}' with mode ('{mode_val}')")

    # --- 3c: Remove duplicate rows ---
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        df = df.drop_duplicates()
        log.append(f"Removed {dup_count} duplicate row(s)")

    # --- 3d: Flag outliers using IQR method ---
    # IQR = Q3 - Q1 (the middle 50% of data)
    # Outlier = any value below Q1 - 1.5*IQR or above Q3 + 1.5*IQR
    # We DON'T remove outliers — we add a boolean column to flag them
    outlier_counts = {}
    for col in numeric_cols:
        if col not in df.columns:
            continue
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - IQR_MULTIPLIER * IQR
        upper_bound = Q3 + IQR_MULTIPLIER * IQR

        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        count = outlier_mask.sum()

        if count > 0:
            outlier_counts[col] = count

    # Add a single "_is_outlier" column: True if ANY numeric column has an outlier in that row
    if outlier_counts:
        outlier_flags = pd.DataFrame(index=df.index)
        for col in outlier_counts:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - IQR_MULTIPLIER * IQR
            upper = Q3 + IQR_MULTIPLIER * IQR
            outlier_flags[col] = (df[col] < lower) | (df[col] > upper)

        df["_is_outlier"] = outlier_flags.any(axis=1)
        total_outliers = df["_is_outlier"].sum()
        details = ", ".join([f"{col}: {cnt}" for col, cnt in outlier_counts.items()])
        log.append(f"Flagged {total_outliers} row(s) as outliers ({details})")
    else:
        df["_is_outlier"] = False

    if not log:
        log.append("No cleaning actions needed — data was already clean!")

    return df, log
