# AI-Powered Business Intelligence Dashboard

An interactive Streamlit dashboard that ingests any CSV/Excel file and produces
KPIs, visualizations, anomaly detection, and AI-generated insights powered by
Claude.

## Features

- Upload any CSV or Excel file and auto-detect column types
- Automatic data cleaning (nulls, duplicates, outlier flags) with a report
- Sidebar filters (date range, category, numeric range)
- KPI metric cards + detailed statistics
- Interactive charts: trend, distribution, composition, category performance,
  anomaly scatter, correlation heatmap
- AI-generated insights from Claude based on the filtered data
- Export filtered data (CSV), full report (HTML), and insights (Markdown)

## Tech Stack

- **Streamlit** — UI layer
- **Pandas / NumPy / SciPy** — data wrangling and statistics
- **Plotly** — interactive charts
- **Anthropic Claude API** — AI insights

## Setup

1. Clone the repo and enter the directory:
   ```bash
   git clone https://github.com/kanishka0109/AI-Business-Intelligence-Dashboard.git
   cd AI-Business-Intelligence-Dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows (Git Bash)
   source venv/Scripts/activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

## Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. Upload a dataset from the sidebar
to begin.

## Project Structure

```
app.py              # Streamlit entry point and UI layout
config.py           # App settings, thresholds, prompt templates
data_loader.py      # File ingestion, type detection, cleaning pipeline
analysis.py         # KPIs, trend/anomaly/correlation computation
visualizations.py   # Plotly chart builders
llm_insights.py     # Claude API integration for AI insights
report_export.py    # CSV / HTML / Markdown export
assets/             # Static assets (CSS)
sample_data/        # Example datasets
```
