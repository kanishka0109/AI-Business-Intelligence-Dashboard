"""
llm_insights.py - Claude API integration and prompt construction.

This module takes computed KPIs and anomaly data, formats them into a
structured prompt, sends it to Claude, and returns business insights.

You'll learn:
  - How to use the Anthropic Python SDK
  - How to design effective prompts for data analysis
  - How to structure LLM input/output for a real application
"""

import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL ,  SYSTEM_PROMPT, USER_PROMPT_TEMPLATE 


def generate_insights(kpi_summary, anomalies, trends , correlation_matrix , category_aggregations):
    """
    Send analysis results to Claude and get business insights.
    Returns a structured response with:
      - Actionable insights
      - Anomaly explanations
      - Trend commentary
      - Executive summary
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    user_prompt = USER_PROMPT_TEMPLATE.format(kpi_summary=kpi_summary,anomalies= anomalies,trends= trends ,correlation_matrix=    correlation_matrix ,category_aggregations= category_aggregations)
    response = client.messages.create(model=CLAUDE_MODEL, max_tokens=1024, system=SYSTEM_PROMPT, messages=[{"role": "user",  "content": user_prompt}])

    # Claude returns one big string. We split it into a list of insights so
    # consumers (like export_insights_markdown) can iterate cleanly.
    raw_text = response.content[0].text

    # Split on newlines → strip whitespace → drop empty lines → strip leading
    # bullet characters ("-", "*", "•") so we don't end up with double bullets.
    insights = [
        line.strip().lstrip("-*•").strip()
        for line in raw_text.split("\n")
        if line.strip()
    ]
    return insights

