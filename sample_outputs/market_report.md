# Tech Sector Q3 Analysis

## Executive Summary
**Offline demo report.** This document was produced without an LLM or live data to verify the
PDF, benchmarking and Pandas pipeline. All figures are *illustrative*. Run `python main.py --query "..."`
with API keys for real research.

## Key Metrics
The sample dataset covers six fictional technology companies across revenue, growth, margin,
R&D spend and valuation. The statistical summary appears in the appendix.

## Analysis
- Revenue is widely dispersed, signalling a market led by a few scaled incumbents.
- Growth ranges from contraction to above 20%, with smaller firms growing fastest.
- Operating margins cluster in the 15-37% band; software-style models sit at the top.

## Risks and Outlook
Valuation multiples vary sharply, so earnings misses may be punished unevenly.

## Sources
Illustrative sample data bundled with the project (`crew/demo.py`).


## Appendix: Statistical Summary

|       |   revenue_busd |   yoy_growth_pct |   operating_margin_pct |   rd_spend_busd |   pe_ratio |
|:------|---------------:|-----------------:|-----------------------:|----------------:|-----------:|
| count |           6    |             6    |                   6    |            6    |       6    |
| mean  |          35.67 |            11.98 |                  24.95 |            5.77 |      29.78 |
| std   |          20.33 |             9.64 |                   7.86 |            2.54 |       8.45 |
| min   |           9.6  |            -3.2  |                  15.4  |            2.2  |      18.9  |
| 25%   |          22.95 |             7.72 |                  20.15 |            4.28 |      23.92 |
| 50%   |          33.15 |            12.7  |                  23.4  |            5.75 |      30.1  |
| 75%   |          48.68 |            17.67 |                  29.58 |            7.38 |      34.33 |
| max   |          64.7  |            24.3  |                  36.8  |            9.2  |      42    |
