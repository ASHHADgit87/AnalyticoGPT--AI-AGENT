# AnalyticoGPT-Agent

**AnalyticoGPT** is an enterprise-grade AI-Agent for data analytics built with **Python, Streamlit, Google ADK, and Gemini AI**. Users upload CSV datasets, and the platform automatically performs data ingestion, cleaning, statistical analysis, visualization, forecasting, AI-powered business insight generation, and executive PDF report creation through a multi-agent workflow.

---

# Google ADK Integration

AnalyticoGPT uses **Google Agent Development Kit (ADK)** to orchestrate an intelligent multi-agent analytics pipeline.

### ADK Usage
- `google.adk.Agent`
- `google.adk.Workflow`
- `AgentRegistry`
- `AgentRouter`
- `AnalysisWorkflowBuilder`
- Gemini-powered reasoning and report generation

### Multi-Agent Workflow

Dataset Detection → Data Cleaning → Statistical Analysis → Visualization → Forecasting → AI Insights → PDF Report Generation

---

# Architecture

AnalyticoGPT follows a **modular multi-tier SaaS architecture**:

- **Frontend:** Streamlit
- **Services:** Pipeline orchestration & dataset management
- **AI Agents:** Google ADK workflow
- **Tools:** Cleaning, Statistics, Visualization, Forecasting, PDF & Gemini
- **Models:** Dataset metadata, analysis results & reports

---

# AaaS

AnalyticoGPT is delivered as a **Agent-as-a-Service (AaaS)** application, enabling users to perform enterprise-scale AI analytics directly from a web browser without local installation.

---

# Features

### Multi-Agent AI Workflow
- 7 specialized AI agents
- Sequential ADK orchestration
- Fully automated analytics pipeline

### Analytics
- Descriptive statistics
- Correlation matrix
- Outlier detection

### Visualization
- Correlation heatmaps
- Trend & scatter plots

### Forecasting
- Linear forecasting
- 5-step future prediction

### AI Insights
- Gemini-generated business insights
- Executive summaries

### Reporting
- Executive PDF reports

---

# Processing Capability

- Processes **entire CSV datasets**
- Supports **unlimited rows & columns**
- Analyzes every numeric and categorical column
- End-to-end automated processing from upload to PDF

### Typical Processing Flow

Upload → Profile → Clean → Analyze → Visualize → Forecast → AI Insights → PDF Report

---

# Scalability

Processing capacity mainly depends on available **RAM**.

| RAM    | Approx Dataset Size |
|--------|--------------------:|
| 8 GB   |    1.5–2 Million Rows |
| 16 GB  |    3–4 Million Rows   |
| 32+ GB |    5+ Million Rows    |

✅1.1 Million records are fully supported.

---

# Statistical & Mathematical Engine

AnalyticoGPT implements a rigorous, research-grade statistical pipeline. Every decision — from correlation method selection to chart type routing — is governed by formal statistical tests and principled mathematical criteria rather than hard-coded heuristics.

### ---> Descriptive Statistics

| Statistic | Formula / Definition | Purpose in Pipeline |
|---|---|---|
| Mean | sum(x) / n | Central tendency; baseline for CV and normality checks |
| Median | Middle value after sorting | Outlier-robust central tendency; used when skew > 1.0 |
| Standard Deviation | sqrt(sum((x - mean)^2) / n) | Spread measure; drives primary metric ranking |
| Skewness | Third standardized moment | Flags non-normal distributions; selects median aggregation in bar charts |
| Excess Kurtosis | Fourth standardized moment minus 3 | Detects heavy tails and extreme outliers beyond standard deviation |
| Min / Max | Boundary values | Range validation and outlier context |

### ---> Normality Testing Ensemble

Before selecting a correlation method, each numeric column is evaluated by a four-test ensemble. The result is determined by majority vote (3 of 4 must agree on normality).

| Test | Valid Sample Range | What It Measures |
|---|---|---|
| Shapiro-Wilk | n < 50 | Exact normality via order statistics |
| D'Agostino-Pearson | 50 to 5,000 | Combined skewness and kurtosis chi-squared statistic |
| Jarque-Bera | All n | Skewness plus kurtosis; valid at any sample size |
| Anderson-Darling | All n (sampled at 10,000) | Tail-weighted distribution fit; more sensitive than KS test |

### ---> Correlation Method Selection

The dominant method across all numeric columns is applied to the entire matrix. Conservative hierarchy: Kendall overrides Spearman, Spearman overrides Pearson.

| Condition | Method Selected | Reason |
|---|---|---|
| n < 30 | Kendall's Tau | Best statistical properties at small n; counts concordant vs discordant pairs |
| Non-normal or skewed | Spearman Rank | Ranks values before correlation; robust to outliers and monotonic non-linearity |
| Normal, n >= 30 | Pearson r | Measures linear co-movement between normally distributed continuous variables |

### Pairwise Minimum Overlap Enforcement

Before computing any pairwise correlation, the pipeline counts rows where both columns are simultaneously non-null. Pairs with fewer than 20 shared observations are set to 0 to prevent spurious correlations driven by sparse data.

### Outlier Detection — Tukey IQR Fence

IQR = Q3 - Q1

Lower fence = Q1 - 1.5 * IQR

Upper fence = Q3 + 1.5 * IQR

Values outside these fences are classified as outliers. Used in the data quality score and descriptive statistics summary. For visualization, values are clipped to the 1st–99th percentile to prevent a single extreme value from compressing the entire chart.

### OLS Linear Regression and Confidence Interval

The trend line chart fits an Ordinary Least Squares regression using closed-form normal equations:

b1 = sum((x - x_mean)(y - y_mean)) / sum((x - x_mean)^2)

b0 = y_mean - b1 * x_mean

y_fit = b0 + b1 * x

The 95% confidence interval for the mean response at each x is:

CI = y_fit +/- t* * s * sqrt(1/n + (x - x_mean)^2 / SSxx)

where s is the residual standard error and t\* is the t-critical value at n-2 degrees of freedom. This is a true regression confidence interval, not a rolling average band.

### Primary Metric Information Score

Each candidate metric column is ranked by a composite information score rather than keyword matching or raw magnitude:

| Component | Weight | Formula |
|---|---|---|
| Coefficient of Variation | 0.40 | std / abs(mean) — scale-invariant dispersion |
| Non-null ratio | 0.30 | non-null rows / total rows |
| Uniqueness ratio | 0.30 | unique values / total rows |
| Keyword bonus | Additive | Domain terms (revenue, sales, profit, etc.) add a fixed bonus |
| Time correlation | Additive | abs(corr with time column) * 10 |

### Data Quality Scoring

Five dimensions are independently scored 0–100 and combined into a weighted final score:

| Dimension | Weight | Measurement |
|---|---|---|
| Completeness | 0.30 | Missing cell percentage |
| Uniqueness | 0.25 | Duplicate row percentage |
| Outlier ratio | 0.20 | IQR-fenced outlier percentage across numeric columns |
| Consistency | 0.15 | Zero-variance or all-null column percentage |
| Skewness load | 0.10 | Average absolute skewness across numeric columns |

Final score maps to a star rating (1–5) and badge: Excellent (90+), Good (75+), Fair (60+), Poor (40+), Critical (below 40).

### Long-to-Wide Format Pivot

Long-format datasets (one row per metric observation) are automatically detected and reshaped using a pivot table:

pivot_table(index=time_col, columns=variable_col, values=value_col, aggfunc='mean')

When the pivot produces more than 20 metric columns, columns are ranked by variance and the top 20 are retained. Variance directly quantifies analytical signal — low-variance columns are dropped.

### Period-over-Period Growth Rate

growth_rate = (current - previous) / previous * 100

Applied across consecutive time steps using pct_change() to identify top-growth periods regardless of absolute magnitude.

### Percentile Rank

Each row's metric value is ranked relative to all other rows:

percentile_rank = rank(pct=True) * 100

A score of 95 means that row's value exceeds 95% of all other observations. Used in the performer analysis report.

### 14-Case Visualization Decision Matrix

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

- **Frontend:** Streamlit
- **Backend:** Python
- **AI Framework:** Google Agent Development Kit (ADK)
- **LLM:** Google Gemini / GenAI
- **Data Processing:** Pandas, NumPy
- **Visualization:** Matplotlib, Seaborn
- **Statistics:** SciPy
- **Report Generation:** ReportLab

---

# Live Demo

https://analyticogpt--ai-agent.streamlit.app/

---

## Creator & Developer

- **Muhammad Ashhadullah Zaheer**
- LinkedIn: https://www.linkedin.com/in/muhammad-ashhadullah-zaheer-41194a340/
