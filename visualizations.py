"""
visualizations.py - Plotly chart builders.

Each function builds one type of interactive chart.
All charts return a Plotly figure object that Streamlit renders via st.plotly_chart().

You'll learn:
  - How to create various Plotly chart types
  - How to customize chart appearance and interactivity
  - How to handle different data shapes for visualization
"""

import plotly.express as px
import plotly.graph_objects as go


def plot_trend_line(df, date_col, value_col, title="Trend Analysis"):
    """Time-series line chart with hover details."""
    fig = px.line(df, x=date_col, y=value_col, title=title)
    return fig


def plot_category_bar(df, category_col, value_col, title="Category Performance"):
    """Horizontal bar chart ranking categories by a metric."""
    fig = px.bar(
        df,
        x=value_col,
        y=category_col,
        title=title,
        color_discrete_sequence=["#636EFA"],
    )
    return fig


def plot_distribution(df, column, title="Distribution"):
    """Histogram with optional box plot overlay."""
    fig = px.histogram(
        df,
        x=column,
        title=title,
        color_discrete_sequence=["#00CC96"],
    )
    return fig


def plot_anomaly_scatter(df, x_col, y_col, anomaly_col, title="Anomaly Detection"):
    """Scatter plot with anomalies highlighted in red."""
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=df[anomaly_col].astype(str),
        title=title,
        color_discrete_map={"True": "#EF553B", "False": "#636EFA"},
        labels={"color": "Outlier"},
    )
    return fig


def plot_correlation_heatmap(corr_matrix, title="Correlation Heatmap"):
    """Color-coded correlation matrix."""
    fig= go.Figure(data=go.Heatmap(z=corr_matrix.values , x=corr_matrix.columns, y=corr_matrix.columns))
    fig.update_layout(title=title)
    return fig


def plot_composition(df, category_col, value_col, title="Composition"):
    """Pie/donut chart for categorical breakdowns."""
    fig = px.pie(df, values=value_col, names=category_col, title=title)
    return fig
