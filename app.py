"""
app.py - Main Streamlit application and UI layout.

This is the entry point. It ties everything together:
  1. File upload sidebar
  2. Data cleaning + cleaning report
  3. Sidebar filters (date, category, numeric)
  4. KPI metric cards
  5. Interactive charts
  6. Anomaly detection + correlation heatmap
  7. Category statistics
  8. AI-generated insights
  9. Export buttons (CSV, HTML, Markdown)

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from config import APP_TITLE, APP_ICON
from data_loader import load_file, clean_data, detect_column_types
from analysis import (
    compute_numeric_kpis,
    detect_anomalies,
    compute_correlation_matrix,
    compute_category_stats,
    detect_trends,
)
from visualizations import (
    plot_trend_line,
    plot_distribution,
    plot_category_bar,
    plot_anomaly_scatter,
    plot_correlation_heatmap,
    plot_composition,
)
from llm_insights import generate_insights
from report_export import export_csv, export_html_report, export_insights_markdown


# --- Page Configuration ---
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load custom CSS ---
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Title ---
st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown(
    "Upload any CSV or Excel file to get instant KPIs, visualizations, "
    "and AI-powered insights."
)
st.markdown("---")

# --- Sidebar: File Upload ---
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Upload a structured dataset to analyze",
    )

# --- Main Content ---
if uploaded_file is None:
    st.info("👈 Upload a dataset from the sidebar to get started.")
else:
    st.success(f"File uploaded: **{uploaded_file.name}**")

    # ── Load and clean ──
    df = load_file(uploaded_file)
    cleaned_df, log = clean_data(df)

    # Cleaning report (collapsed by default)
    with st.expander("🧹 Cleaning Report", expanded=False):
        for msg in log:
            st.write("• " + msg)

    # Detect column types (used for filters AND charts)
    col_types = detect_column_types(cleaned_df)

    # ── Sidebar filters ──
    with st.sidebar:
        st.markdown("---")
        st.header("🔎 Filters")

        filtered_df = cleaned_df.copy()

        # Date range filter
        if col_types["datetime"]:
            date_col = col_types["datetime"][0]
            min_date = cleaned_df[date_col].min().date()
            max_date = cleaned_df[date_col].max().date()
            date_range = st.date_input(
                f"Date range ({date_col})",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start, end = date_range
                filtered_df = filtered_df[
                    (filtered_df[date_col] >= pd.Timestamp(start))
                    & (filtered_df[date_col] <= pd.Timestamp(end))
                ]

        # Categorical multi-select filter
        if col_types["categorical"]:
            cat_col = col_types["categorical"][0]
            unique_values = sorted(cleaned_df[cat_col].dropna().unique().tolist())
            selected = st.multiselect(
                f"{cat_col}",
                options=unique_values,
                default=unique_values,
            )
            if selected:
                filtered_df = filtered_df[filtered_df[cat_col].isin(selected)]

        # Numeric range slider
        if col_types["numeric"]:
            num_col_filter = col_types["numeric"][0]
            min_val = float(cleaned_df[num_col_filter].min())
            max_val = float(cleaned_df[num_col_filter].max())
            if min_val < max_val:
                num_range = st.slider(
                    f"{num_col_filter} range",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                )
                filtered_df = filtered_df[
                    (filtered_df[num_col_filter] >= num_range[0])
                    & (filtered_df[num_col_filter] <= num_range[1])
                ]

        # Reset (rerun the script)
        if st.button("🔄 Reset filters"):
            st.rerun()

    # ── Filter status ──
    st.caption(
        f"Showing **{len(filtered_df):,}** of **{len(cleaned_df):,}** rows after filters."
    )

    # ── Data preview (collapsed) ──
    with st.expander("📂 Filtered Data Preview", expanded=False):
        st.dataframe(filtered_df, use_container_width=True)

    # ── KPI Metric Cards ──
    st.markdown("---")
    st.subheader("📊 Key Metrics")
    if col_types["numeric"]:
        metric_cols = col_types["numeric"][:4]  # show up to 4 metrics
        cols = st.columns(len(metric_cols))
        for i, col in enumerate(metric_cols):
            with cols[i]:
                avg_val = filtered_df[col].mean()
                total_val = filtered_df[col].sum()
                st.metric(
                    label=f"Avg {col}",
                    value=f"{avg_val:,.2f}",
                    delta=f"Total: {total_val:,.0f}",
                )

    # Detailed KPI table
    kpis = compute_numeric_kpis(filtered_df)
    with st.expander("📋 Detailed Statistics"):
        st.dataframe(kpis, use_container_width=True)

    # Charts list (for the HTML export)
    charts = []

    # ── Trend chart ──
    st.markdown("---")
    st.subheader("📈 Trend Analysis")
    if col_types["datetime"] and col_types["numeric"]:
        date_col = col_types["datetime"][0]
        num_col = col_types["numeric"][0]
        fig = plot_trend_line(filtered_df, date_col, num_col)
        charts.append(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No date column found — skipping trend chart.")

    # ── Distribution + Composition (side by side) ──
    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Distribution")
        if col_types["numeric"]:
            num_col = col_types["numeric"][0]
            fig = plot_distribution(filtered_df, num_col)
            charts.append(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric column.")

    with col_b:
        st.subheader("🥧 Composition")
        if col_types["categorical"] and col_types["numeric"]:
            cat_col = col_types["categorical"][0]
            val_col = col_types["numeric"][0]
            fig = plot_composition(filtered_df, cat_col, val_col)
            charts.append(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need a category + numeric column.")

    # ── Category bar chart ──
    st.markdown("---")
    st.subheader("📊 Category Performance")
    if col_types["categorical"] and col_types["numeric"]:
        cat_col = col_types["categorical"][0]
        val_col = col_types["numeric"][0]
        fig = plot_category_bar(filtered_df, cat_col, val_col)
        charts.append(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category column found — skipping bar chart.")

    # ── Anomaly scatter ──
    st.markdown("---")
    st.subheader("🚨 Anomaly Detection")
    if len(col_types["numeric"]) >= 2 and "_is_outlier" in filtered_df.columns:
        x_col = col_types["numeric"][0]
        y_col = col_types["numeric"][1]
        fig = plot_anomaly_scatter(filtered_df, x_col, y_col, "_is_outlier")
        charts.append(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need at least 2 numeric columns for the anomaly scatter plot.")

    # Anomaly counts (collapsed)
    if col_types["numeric"]:
        anomalies = detect_anomalies(filtered_df)
        with st.expander("Anomaly counts per column"):
            st.dataframe(anomalies["count"], use_container_width=True)
    else:
        anomalies = None

    # ── Correlation heatmap ──
    st.markdown("---")
    st.subheader("🔥 Correlation Heatmap")
    if len(col_types["numeric"]) >= 2:
        corr_matrix = compute_correlation_matrix(filtered_df)
        fig = plot_correlation_heatmap(corr_matrix)
        charts.append(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        corr_matrix = None
        st.info("Need at least 2 numeric columns for a correlation heatmap.")

    # ── Category Statistics ──
    st.markdown("---")
    st.subheader("📑 Category Statistics")
    category_aggregations = compute_category_stats(filtered_df)
    if category_aggregations:
        cat_stats_df = pd.DataFrame(category_aggregations).T
        st.dataframe(cat_stats_df, use_container_width=True)
    else:
        st.info("No categorical columns found.")

    # ── Trends (computed for AI insights) ──
    if col_types["datetime"] and col_types["numeric"]:
        trends = detect_trends(
            filtered_df, col_types["datetime"][0], col_types["numeric"][0]
        )
    else:
        trends = None

    # ── AI Insights ──
    st.markdown("---")
    st.subheader("🤖 AI Insights")
    try:
        with st.spinner("Claude is analyzing your data..."):
            insights = generate_insights(
                kpis, anomalies, trends, corr_matrix, category_aggregations
            )
        with st.container(border=True):
            for insight in insights:
                st.markdown(f"- {insight}")
    except Exception:
        insights = []
        st.warning("AI insights unavailable.")

    # ── Export buttons ──
    st.markdown("---")
    st.subheader("📥 Export")

    csv_data = export_csv(filtered_df)
    html_report = export_html_report(kpis, charts, insights)
    md_insights = export_insights_markdown(insights)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            label="📄 Filtered Data (CSV)",
            data=csv_data,
            file_name="filtered_data.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            label="🌐 Full Report (HTML)",
            data=html_report,
            file_name="report.html",
            mime="text/html",
            use_container_width=True,
        )
    with c3:
        st.download_button(
            label="📝 Insights (Markdown)",
            data=md_insights,
            file_name="insights.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # ── Footer ──
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; opacity: 0.5; padding: 20px 0;'>"
        "Built with Streamlit & Claude AI"
        "</div>",
        unsafe_allow_html=True,
    )
