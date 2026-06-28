# AnalyticoGPT-Agent

**AnalyticoGPT** is an enterprise-grade AI-Agent for data analytics built with **Python, Streamlit, Google ADK, and Gemini AI**. Users upload CSV datasets, and the platform automatically performs data ingestion, cleaning, statistical analysis, visualization, forecasting, AI-powered business insight generation, and executive PDF report creation through a multi-agent workflow.

---

# Google ADK Integration

AnalyticoGPT uses **Google Agent Development Kit (ADK)** to orchestrate an intelligent multi-agent analytics pipeline.

### ADK Usage

| Component | Role |
|---|---|
| `google.adk.Agent` | Base agent class for each specialized worker |
| `google.adk.Workflow` | Orchestrates sequential agent execution |
| `AgentRegistry` | Registers and resolves agents by name |
| `AgentRouter` | Routes tasks to the correct agent |
| `AnalysisWorkflowBuilder` | Constructs the full analytics pipeline |
| Gemini-powered reasoning | AI narrative, insight generation, report text |

### Multi-Agent Workflow

```
Dataset Detection → Data Cleaning → Statistical Analysis → Visualization → Forecasting → AI Insights → PDF Report Generation
```

---

# Architecture

AnalyticoGPT follows a **modular multi-tier SaaS architecture**:

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Services | Pipeline orchestration & dataset management |
| AI Agents | Google ADK workflow |
| Tools | Cleaning, Statistics, Visualization, Forecasting, PDF & Gemini |
| Models | Dataset metadata, analysis results & reports |

---

# AaaS

AnalyticoGPT is delivered as an **Agent-as-a-Service (AaaS)** application, enabling users to perform enterprise-scale AI analytics directly from a web browser without local installation.

---

# Features

### Multi-Agent AI Workflow

| Capability | Detail |
|---|---|
| Agent count | 7 specialized AI agents |
| Orchestration | Sequential ADK pipeline |
| Automation | Fully automated from upload to PDF |
| Prompt engineering | Context-aware Gemini prompts include skewness, kurtosis, quality scores, forecast values, chart context, bottom performers, and growth leaders |
| Narrative enforcement | Gemini instructed to output plain professional prose — no markdown symbols in PDF output |

### Analytics

| Capability | Detail |
|---|---|
| Descriptive statistics | Mean, median, std, skewness, excess kurtosis, min, max per column |
| Correlation matrix | Pearson / Spearman / Kendall selected automatically per dataset |
| Outlier detection | Tukey IQR fence with 1st–99th percentile clipping for display |
| Aggregation switching | Bar charts auto-select median when `abs(skew) > 1.0`, mean otherwise |
| Overlap enforcement | Pairs with fewer than 20 shared non-null rows set to 0.0 — no spurious coefficients |
| Heatmap suppression | Heatmap skipped when max `\|r\| < 0.15` across all pairs |
| Binary column exclusion | Columns where `nunique ≤ 2` and `range ≤ 1` excluded from primary metric selection |
| Primary metric ranking | Composite score: CV + completeness + keyword bonus + time correlation |
| Performer analysis | Top performers, bottom performers, percentile rank, top growth leaders per dataset |
| Growth rate | Period-over-period `pct_change()` across consecutive time steps |

### Visualization

| Capability | Detail |
|---|---|
| Correlation heatmap | Magma colormap, method label in title, column name wrapping |
| Trend line chart | Actual trend + OLS regression line + 95% CI band |
| Bar chart | Sorted descending, top 20 cap, skewness-driven aggregation |
| Epoch bug prevention | Integer year columns (1900–2100) kept as plain integers, never passed through `pd.to_datetime()` |
| Fiscal quarter detection | Recognises formats like `2019-Q1`, `2020-Q3` as temporal columns |
| Outlier clipping | Display clipped to 1st–99th percentile; source data never mutated |
| High-cardinality fast path | `value_counts().head(20)` used for large datasets to avoid full groupby |
| Label wrapping | Long axis labels wrapped with `textwrap` to prevent overlap |

### Forecasting

| Method | Priority | Notes |
|---|---|---|
| Holt Damped Double Exponential Smoothing | Primary | Trend-aware; handles dampening |
| Simple Exponential Smoothing | Fallback | Baseline smoothing when Holt fails |
| Linear OLS Extrapolation | Final fallback | Always available; no dependency |

- All successful methods returned simultaneously with forecasts and labels
- `best_method` field identifies most sophisticated method that succeeded
- Graceful degradation — if `statsmodels` unavailable, falls back to linear automatically
- 5-step future prediction with directional trajectory label (upward / downward)

### Data Quality Scoring

| Dimension | Weight | Measurement |
|---|---|---|
| Completeness | 30% | Missing cell percentage |
| Uniqueness | 25% | Duplicate row percentage |
| Outlier ratio | 20% | IQR-fenced outlier % across numeric columns |
| Consistency | 15% | Zero-variance or all-null column percentage |
| Skewness load | 10% | Average absolute skewness across numeric columns |

| Score Range | Star Rating | Badge |
|---|---|---|
| 90 – 100 | ⭐⭐⭐⭐⭐ | Excellent |
| 75 – 89 | ⭐⭐⭐⭐☆ | Good |
| 60 – 74 | ⭐⭐⭐☆☆ | Fair |
| 40 – 59 | ⭐⭐☆☆☆ | Poor |
| 0 – 39 | ⭐☆☆☆☆ | Critical |

- Raw stats reported: total rows, columns, missing cells, duplicate rows, bad columns
- Quality context injected into Gemini prompt for AI-aware narrative commentary

### AI Insights

| Capability | Detail |
|---|---|
| Narrative generation | Gemini writes 4–6 paragraph professional analytical narrative |
| Context injected | Skewness, kurtosis, quality score, forecast values, chart context, top/bottom performers, growth leaders |
| Plain prose enforcement | `system_instruction` forbids markdown symbols — output is PDF-safe |
| Fallback | If API key missing or call fails, structured summary rendered instead |

### Reporting — PDF

| Section | Content |
|---|---|
| Header | Title, subtitle, indigo rule line |
| Dataset Summary | Processed fields, metric/feature columns, correlation method, unit, flags |
| AI Narrative | Gemini prose with markdown stripped clean |
| Data Quality Scorecard | Color-coded score, star rating, badge, raw stats, five segmented dimension bars |
| Top Performers Table | NaN/None/NaT auto-cleaned, all-null columns dropped, snake_case → Title Case headers |

- Score color-coded: green (Excellent), amber (Fair), red (Poor/Critical)
- All `**`, `*`, `#`, `` ` `` stripped before rendering — no symbols appear in PDF

### Long Format & Data Shape Handling

| Capability | Detail |
|---|---|
| Auto-detection | Token matching on value, variable, unit, time, category column names |
| Pivot reshaping | `pivot_table(index=time_col, columns=variable_col, values=value_col, aggfunc='mean')` |
| Column pruning | When pivot > 20 columns, top 20 by variance retained |
| Mixed unit detection | Currency, percentage, and count types detected — dominant unit isolated |
| Sparse dataset tolerance | Valid ratio threshold 0.3 to handle placeholder rows like `"..."` |

---

# Processing Capability

| Capability | Detail |
|---|---|
| Dataset support | Entire CSV files, unlimited rows and columns |
| Column handling | Every numeric and categorical column analyzed automatically |
| Large dataset sampling | Trend charts sample to 1,000 points; bar charts use `value_counts` fast path |
| Processing flow | Upload → Profile → Clean → Analyze → Visualize → Forecast → AI Insights → PDF |

### Scalability

| RAM | Approx Dataset Size |
|---|---|
| 8 GB | 1.5–2 Million Rows |
| 16 GB | 3–4 Million Rows |
| 32+ GB | 5+ Million Rows |

✅ 5 Million records are fully supported.

---

# Statistical & Mathematical Engine

AnalyticoGPT implements a rigorous, research-grade statistical pipeline. Every decision — from correlation method selection to chart type routing — is governed by formal statistical tests and principled mathematical criteria rather than hard-coded heuristics.

### ---> Descriptive Statistics

| Statistic | Formula | Purpose in Pipeline |
|---|---|---|
| Mean | `sum(x) / n` | Central tendency; baseline for CV and normality checks |
| Median | Middle value after sorting | Outlier-robust central tendency; used when skew > 1.0 |
| Standard Deviation | `sqrt(sum((x - mean)^2) / n)` | Spread measure; drives primary metric ranking |
| Skewness | Third standardized moment | Flags non-normal distributions; selects median aggregation in bar charts |
| Excess Kurtosis | Fourth standardized moment minus 3 | Detects heavy tails and extreme outliers beyond standard deviation |
| Min / Max | Boundary values | Range validation and outlier context |

### ---> Normality Testing Ensemble

Before selecting a correlation method, each numeric column is evaluated by a four-test ensemble. The result is determined by majority vote — 3 of 4 must agree on normality.

| Test | Valid Sample Range | What It Measures | Notes |
|---|---|---|---|
| Shapiro-Wilk | n < 50 | Exact normality via order statistics | Most powerful for small n |
| D'Agostino-Pearson | 50 to 5,000 | Combined skewness and kurtosis chi-squared statistic | Omnibus test |
| Jarque-Bera | All n | Skewness plus kurtosis; valid at any sample size | Fast; O(n) |
| Skewness + Kurtosis heuristic | All n | `abs(skew) < 1.0 and abs(kurt) < 3.5` | Replaces Anderson-Darling for SciPy 1.17+ compatibility; no FutureWarning |

### ---> Correlation Method Selection

The dominant method across all numeric columns is applied to the entire matrix. Conservative hierarchy: Kendall overrides Spearman, Spearman overrides Pearson.

| Condition | Method Selected | Reason |
|---|---|---|
| n < 30 | Kendall's Tau | Best statistical properties at small n; counts concordant vs discordant pairs |
| Non-normal or skewed | Spearman Rank | Ranks values before correlation; robust to outliers and monotonic non-linearity |
| Normal, n ≥ 30 | Pearson r | Measures linear co-movement between normally distributed continuous variables |

### ---> Pairwise Minimum Overlap Enforcement

Before computing any pairwise correlation, the pipeline counts rows where both columns are simultaneously non-null. Pairs with fewer than 20 shared observations are **set to 0.0** (not omitted) to prevent spurious correlations driven by sparse data.

### ---> Outlier Detection — Tukey IQR Fence

```
IQR = Q3 - Q1
Lower fence = Q1 - 1.5 * IQR
Upper fence = Q3 + 1.5 * IQR
```

Values outside these fences are classified as outliers. Used in the data quality score and descriptive statistics summary. For visualization, values are clipped to the 1st–99th percentile to prevent a single extreme value from compressing the entire chart.

### ---> OLS Linear Regression and Confidence Interval

The trend line chart fits an Ordinary Least Squares regression using closed-form normal equations:

```
b1 = sum((x - x_mean)(y - y_mean)) / sum((x - x_mean)^2)
b0 = y_mean - b1 * x_mean
y_fit = b0 + b1 * x
```

The 95% confidence interval for the mean response at each x is:

```
CI = y_fit ± t* × s × sqrt(1/n + (x - x_mean)^2 / SSxx)
```

where `s` is the residual standard error and `t*` is the t-critical value at n-2 degrees of freedom. This is a **true regression confidence interval**, not a rolling average band.

### ---> Primary Metric Information Score

Binary columns where `nunique ≤ 2` and `range ≤ 1` are excluded before scoring to prevent flag/cancelled-type columns from being selected.

| Component | Weight | Formula |
|---|---|---|
| Coefficient of Variation | 0.40 | `std / abs(mean)` — scale-invariant dispersion |
| Non-null ratio | 0.30 | `non-null rows / total rows` |
| Uniqueness ratio | 0.30 | `unique values / total rows` |
| Keyword bonus | Additive | Domain terms (revenue, sales, profit, etc.) add a fixed bonus |
| Time correlation | Additive | `abs(corr with time column) × 10` |

### ---> Data Quality Scoring

Five dimensions are independently scored 0–100 and combined into a weighted final score:

| Dimension | Weight | Measurement |
|---|---|---|
| Completeness | 0.30 | Missing cell percentage |
| Uniqueness | 0.25 | Duplicate row percentage |
| Outlier ratio | 0.20 | IQR-fenced outlier percentage across numeric columns |
| Consistency | 0.15 | Zero-variance or all-null column percentage |
| Skewness load | 0.10 | Average absolute skewness across numeric columns |

Final score maps to a star rating (1–5) and badge: Excellent (90+), Good (75+), Fair (60+), Poor (40+), Critical (below 40).

### ---> Long-to-Wide Format Pivot

Long-format datasets (one row per metric observation) are automatically detected and reshaped:

```
pivot_table(index=time_col, columns=variable_col, values=value_col, aggfunc='mean')
```

When the pivot produces more than 20 metric columns, columns are ranked by variance and the top 20 are retained. Variance directly quantifies analytical signal — low-variance columns are dropped.

### ---> Period-over-Period Growth Rate

```
growth_rate = (current - previous) / previous × 100
```

Applied across consecutive time steps using `pct_change()` to identify top-growth periods regardless of absolute magnitude.

### ---> Percentile Rank

```
percentile_rank = rank(pct=True) × 100
```

A score of 95 means that row's value exceeds 95% of all other observations. Used in the performer analysis report.

### ---> Skewness-Based Aggregation Switching

```
aggregation = 'median' if abs(skew) > 1.0 else 'mean'
```

Applied automatically to bar charts. Median is more robust to extreme outliers and gives a better picture of the typical value per group when distributions are heavily skewed.

### ---> Integer Year Epoch Prevention

Integer columns whose values fall entirely in the range 1900–2100 are recognised as temporal and kept as plain integers. They are **never** passed through `pd.to_datetime()`, which would interpret them as nanoseconds since the Unix epoch and produce labels like `1970-01-01 00:00:00.0000002016`.

### ---> 14-Case Visualization Decision Matrix

Chart type is selected deterministically based on data structure profiling, not user input.

| Edge Case | Profile | Heatmap | Trend | Bar |
|---|---|---|---|---|
| EC-01 | Zero numeric columns | No | No | No |
| EC-02 | One numeric, no anchor | No | No | No |
| EC-03 | Multiple numeric, no time/category | Yes | No | No |
| EC-04 | Time + incompatible mixed-unit metric | No | No | No |
| EC-05 | Time + one valid metric | No | Yes | No |
| EC-06 | Multiple metrics + time | Yes | Yes | No |
| EC-07 | One categorical + one metric | No | No | Yes |
| EC-08 | High-cardinality categorical + metric | No | No | Yes (Top 20) |
| EC-09 | All zero variance | No | No | No |
| EC-10 | Low-cardinality time + multi-metrics | Yes | Yes | Yes |
| EC-11 | Ordered categorical + multi-metrics | Yes | Yes | Yes |
| EC-12 | Time + categories + multi-metrics | Yes | Yes | Yes |
| EC-13 | Financial portfolio structure | Yes | Yes | Yes |
| EC-14 | A/B test matrix | Yes | Yes | Yes |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| AI Framework | Google Agent Development Kit (ADK) |
| LLM | Google Gemini / GenAI |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Statistics | SciPy |
| Forecasting | statsmodels (Holt, SimpleExpSmoothing) with linear OLS fallback |
| Report Generation | ReportLab — custom ParagraphStyle, HRFlowable, nested Table layouts |

---

# Live Demo

https://analyticogpt--ai-agent.streamlit.app/

---

## Creator & Developer

- **Muhammad Ashhadullah Zaheer**
- LinkedIn: https://www.linkedin.com/in/muhammad-ashhadullah-zaheer-41194a340/
