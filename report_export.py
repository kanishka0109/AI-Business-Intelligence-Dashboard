"""
report_export.py - HTML/CSV report generation and download handlers.

Generates downloadable reports from the current dashboard state.
All exports respect active filters.

You'll learn:
  - How to generate HTML reports programmatically
  - How to create download buttons in Streamlit
  - How to bundle charts and text into a single report
"""

import copy
import pandas as pd


def export_csv(df):
    """Convert filtered DataFrame to downloadable CSV."""
    result = df.to_csv(index=False)
    return result


def export_html_report(kpis, charts, insights):
    """Generate a styled HTML report with KPIs, charts, and AI narrative."""

    # ── 1. KPI section ─────────────────────────────────────────
    # `kpis` is a pandas DataFrame (from analysis.compute_numeric_kpis).
    # DataFrames have a built-in .to_html() method that returns a complete
    # <table>...</table> string. We pass classes="kpi-table" so our CSS below
    # can style it, and border=0 to suppress pandas' default border attribute.
    kpi_html = kpis.to_html(classes="kpi-table", border=0)

    # ── 2. Charts section ─────────────────────────────────────
    # `charts` is a list of Plotly Figure objects.
    # Each figure has a .to_html() method that returns an interactive <div>.
    # IMPORTANT: Plotly's JS library is ~3MB. We only want to load it ONCE,
    # so we use include_plotlyjs="cdn" on the FIRST chart (loads from CDN)
    # and False for the rest (they reuse the already-loaded library).
    #
    # We deepcopy each figure and override the template to "plotly_white"
    # so charts render with a light background and colorful traces in the
    # HTML report (Streamlit's dark theme would otherwise make them black).
    charts_html = ""
    for i, fig in enumerate(charts):
        fig_copy = copy.deepcopy(fig)
        fig_copy.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
        include_js = "cdn" if i == 0 else False
        charts_html += fig_copy.to_html(full_html=False, include_plotlyjs=include_js)

    # ── 3. Insights section ───────────────────────────────────
    # `insights` is now a list of strings (after our llm_insights.py fix).
    # We wrap each insight in <li> tags inside a <ul> for a clean bullet list.
    insights_html = "<ul>" + "".join(f"<li>{item}</li>" for item in insights) + "</ul>"

    # ── 4. Assemble the full HTML document ────────────────────
    # Note the DOUBLE braces {{ }} in the CSS — inside an f-string, {{ means
    # a literal { character. Single { would be interpreted as a variable.
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Business Intelligence Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
            background: #fafafa;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
        }}
        .kpi-table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            background: white;
        }}
        .kpi-table th, .kpi-table td {{
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        .kpi-table th {{
            background: #3498db;
            color: white;
        }}
        .kpi-table tr:nth-child(even) {{
            background: #f2f2f2;
        }}
        ul li {{
            margin: 8px 0;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <h1>AI Business Intelligence Report</h1>

    <h2>Key Metrics</h2>
    {kpi_html}

    <h2>Visualizations</h2>
    {charts_html}

    <h2>AI Insights</h2>
    {insights_html}
</body>
</html>"""

    return html



def export_insights_markdown(insights):
    """Export just the AI-generated insights as markdown."""
    text = "# AI - Generated Insights\n\n"
    for i in insights:
        text = text + " - " + i +"\n"
    return text
