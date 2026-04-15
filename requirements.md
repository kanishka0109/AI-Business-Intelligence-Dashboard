# AI-Powered Business Intelligence Dashboard

A GenAI-enabled analytics platform that transforms raw business datasets into interactive dashboards, automated KPI tracking, anomaly detection, and LLM-generated insights — all through a clean, no-code web interface built with Streamlit.

---

## Project Overview

Most small and mid-size businesses sit on valuable data but lack the tools or expertise to extract insights from it. This dashboard bridges that gap. Upload any structured dataset (CSV or Excel), and the system automatically cleans it, computes relevant KPIs, visualizes trends, flags anomalies, and generates plain-English business recommendations powered by Claude's API.

The entire pipeline is zero-config — no column mapping, no manual setup. The system infers data types, adapts its analysis, and presents everything through an interactive UI.

---

## Core Features

### 1. Smart Data Ingestion & Auto-Cleaning

The system accepts CSV and Excel files and runs an automated cleaning pipeline:

- Detects and parses date columns regardless of format
- Infers column types (numeric, categorical, datetime, boolean)
- Drops columns exceeding a configurable null threshold (default: 50%)
- Imputes missing numeric values with median, categorical with mode
- Removes duplicate rows and logs all cleaning actions
- Flags statistical outliers using the IQR method
- Presents a transparent cleaning report showing exactly what changed

### 2. Dynamic KPI Engine

Based on the detected schema, the system auto-generates relevant business metrics:

- **Numeric Columns**: mean, median, standard deviation, min/max, month-over-month percentage change, YoY growth where applicable
- **Categorical Columns**: unique count, top categories by frequency, concentration ratio (top 3 share percentage)
- **Date × Numeric Combinations**: trend direction via linear regression slope, moving averages, seasonality indicators
- **Cross-Column**: correlation matrix across all numeric fields, category-wise aggregation of any selected metric

KPIs are displayed as interactive metric cards with delta indicators showing period-over-period change.

### 3. Interactive Visualizations

All charts are built with Plotly for full interactivity (zoom, hover, pan, export):

- **Trend Analysis**: Time-series line charts with configurable granularity (daily, weekly, monthly, quarterly)
- **Category Performance**: Horizontal bar charts ranking categories by any selected metric
- **Distribution Analysis**: Histograms and box plots for understanding data spread
- **Anomaly Scatter Plot**: Data points plotted with anomalies highlighted in red, including hover details
- **Correlation Heatmap**: Color-coded matrix showing relationships between all numeric variables
- **Composition Charts**: Pie/donut charts for categorical breakdowns

### 4. LLM-Powered Business Insights

The computed KPIs, anomaly flags, and trend data are sent to Claude's API with a structured prompt. The LLM returns:

- 3 to 5 actionable business insights grounded in the actual numbers
- Anomaly explanations with possible business causes
- Trend commentary with forward-looking suggestions
- A concise executive summary suitable for stakeholder communication

Users can regenerate insights with a single click, and the prompt adapts based on which filters and date ranges are active.

### 5. Filtering & Drill-Down

The sidebar provides dynamic filters that update every chart and KPI in real time:

- Date range selector (calendar picker)
- Categorical column filters (multi-select dropdowns, auto-populated from data)
- Numeric range sliders for threshold-based filtering
- A reset button to clear all filters at once

### 6. Exportable Reports

Generate downloadable reports that bundle the current dashboard state:

- **CSV Export**: Cleaned and filtered dataset
- **HTML Report**: Styled report with KPI summary table, embedded charts, and the LLM-generated narrative
- **Insights Export**: Plain-text or markdown file of just the AI-generated insights

All exports respect the currently applied filters, so users get exactly the slice they are viewing.

---

## Tech Stack

### Language & Runtime

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Package Manager | pip with venv |

### Data Processing

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Pandas | v2.0+ | Data loading, cleaning, transformation, aggregation |
| NumPy | v1.24+ | Statistical computations, outlier detection, array operations |
| SciPy | v1.11+ | Linear regression for trend detection, statistical tests |

### Visualization

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Plotly | v5.18+ | Interactive charts (line, bar, scatter, heatmap, pie) |
| Streamlit native charts | Built-in | Quick metric cards and simple displays |

### Frontend & UI

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Streamlit | v1.30+ | Web application framework, layout, widgets, file upload, session state |
| Custom CSS | Injected via st.markdown | Styling overrides for cards, spacing, and theming |

### AI / LLM Integration

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Anthropic Python SDK | v0.30+ | Claude API client for generating business insights |
| Claude Sonnet | claude-sonnet-4-20250514 | LLM model used for natural language insight generation |
| Prompt Engineering | Custom system + user prompts | Structured prompt templates that feed KPIs to the LLM |

### Utilities

| Component | Technology | Purpose |
|-----------|-----------|---------|
| openpyxl | v3.1+ | Reading and writing Excel (.xlsx) files |
| python-dotenv | v1.0+ | Environment variable management for API keys |

---

## Project Structure

```
bi-dashboard/
│
├── app.py                  # Main Streamlit application and UI layout
├── data_loader.py          # File ingestion, type detection, auto-cleaning pipeline
├── analysis.py             # KPI computation, anomaly detection, trend analysis
├── visualizations.py       # Plotly chart builders (trend, bar, scatter, heatmap)
├── llm_insights.py         # Claude API integration and prompt construction
├── report_export.py        # HTML/CSV report generation and download handlers
├── config.py               # App configuration, thresholds, prompt templates
│
├── sample_data/
│   └── superstore.csv      # Demo dataset for testing
│
├── assets/
│   └── style.css           # Custom styling for the Streamlit UI
│
├── .env                    # API keys (not committed to version control)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Data Flow Pipeline

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  CSV / XLSX  │────▶│  Data Loader     │────▶│  Clean Dataset  │
│  Upload      │     │  (Auto-clean)    │     │  + Cleaning Log │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  Analysis Engine │
                                              │  (KPIs, Trends,  │
                                              │   Anomalies)     │
                                              └────────┬────────┘
                                                       │
                                          ┌────────────┼────────────┐
                                          ▼            ▼            ▼
                                   ┌───────────┐ ┌──────────┐ ┌──────────┐
                                   │  Plotly   │ │  Claude  │ │  Export  │
                                   │  Charts   │ │  API     │ │  Engine  │
                                   └─────┬─────┘ └────┬─────┘ └────┬─────┘
                                         │            │            │
                                         ▼            ▼            ▼
                                   ┌──────────────────────────────────────┐
                                   │       Streamlit Dashboard UI         │
                                   │  (Charts + KPI Cards + AI Insights   │
                                   │   + Filters + Export Buttons)        │
                                   └──────────────────────────────────────┘
```

---

## Key Technical Decisions

**Why Streamlit over Dash or Flask?**
Streamlit gives the fastest path from Python script to interactive web app. No frontend code, no callbacks wiring, no HTML templates. For a data-focused dashboard, it is the right trade-off — rapid development with a polished result.

**Why Plotly over Matplotlib?**
Plotly charts are interactive out of the box — hover tooltips, zoom, pan, and PNG export. Matplotlib produces static images that feel flat in a web dashboard. Plotly also integrates natively with Streamlit via `st.plotly_chart`.

**Why Claude over OpenAI?**
Claude handles structured data interpretation well, produces clear business language, and follows system prompt instructions precisely — important when the prompt includes JSON-formatted KPIs that need to be referenced accurately in the output.

**Why auto-detection over manual column mapping?**
The entire value proposition is zero-config. A user uploads a file and gets insights. Manual mapping adds friction and limits the audience to technical users. Auto-detection via `pandas.api.types` and heuristic rules makes the tool accessible to anyone.

---

## Environment Variables

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
```

Stored in `.env`, loaded via `python-dotenv`, never committed to version control.

---

## How to Run

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-bi-dashboard.git
cd ai-bi-dashboard

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Launch the dashboard
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Future Enhancements

- **Multi-file joins**: Upload multiple CSVs and define relationships for cross-dataset analysis
- **Scheduled reports**: Email automated weekly insight summaries
- **Database connectors**: Pull data directly from PostgreSQL, MySQL, or BigQuery
- **Custom KPI definitions**: Let users define their own calculated metrics via a formula builder
- **Conversational interface**: Chat with your data using a Claude-powered Q&A panel
- **Role-based views**: Different dashboard layouts for executives vs analysts vs operations