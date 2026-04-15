"""
config.py - Central configuration for the BI Dashboard.

This module holds all app-wide settings, thresholds, and prompt templates.
Keeping config separate means you can tweak behavior without touching logic code.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Configuration ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# --- Data Cleaning Thresholds ---
NULL_THRESHOLD = 0.5  # Drop columns with more than 50% nulls
IQR_MULTIPLIER = 1.5  # For outlier detection: values beyond Q1 - 1.5*IQR or Q3 + 1.5*IQR

# --- App Settings ---
APP_TITLE = "AI-Powered Business Intelligence Dashboard"
APP_ICON = "📊"
MAX_FILE_SIZE_MB = 200

# --- LLM Prompt Templates ---
SYSTEM_PROMPT = """act like a senior business analyst you will recieve the KPI summaries , anomaly flags and trend data your job is to analyse these and generate actionable insights , determine the trend pattern present in the data and suggest next steps keep your responses concise ,explain anamolies dont assume anything it should be data backed avoid jargons and based on facts"""

USER_PROMPT_TEMPLATE = """Analyze the following dataset insights carefully.

### Input Data

KPI Summary:
{kpi_summary}

Detected Anomalies:
{anomalies}

Trend Analysis:
{trends}

Correlation Matrix:
{correlation_matrix}

Category-wise Aggregations:
{category_aggregations}

---

### Task

Using only the data provided above, generate a structured analysis.

### Output Format

1. Executive Summary

* Explain the overall dataset and key columns in 2–3 simple sentences.

2. Trend Analysis

* Describe the trend direction clearly (increasing, decreasing, stable).
* Explain in simple terms whether the trend is positive (profitable) or negative (risky/backfiring).

3. Anomaly Insights

* Identify what looks unusual or suspicious.
* Explain possible reasons based only on the data.

4. Correlation Insights

* Briefly explain important relationships between variables.
* Highlight strong positive or negative correlations.

5. Category-wise Insights

* Summarize key differences or patterns across categories.

---

### Constraints

* Keep explanations simple and easy to understand.
* Do NOT assume anything outside the given data.
* Every insight must be supported by the provided data.
* Be concise but meaningful.
"""

# --- Time Granularity ---
TIME_GRANULARITY_OPTIONS = ["Daily", "Weekly", "Monthly", "Quarterly"]

# --- Visualization Settings ---
DEFAULT_CHART_HEIGHT = 400
DEFAULT_COLOR_PALETTE = "Set2"