import re
import textwrap
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import scipy.stats as scipy_stats


def _coerce_numeric_series(series: pd.Series) -> pd.Series:
    """Coerce any series to float, handling comma-formatted numbers and currency symbols."""
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    if pd.api.types.is_datetime64_any_dtype(series):
        return pd.Series(dtype=float, index=series.index)
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace(r"[^0-9.\-]", "", regex=True)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def _is_id_like_column(col_name: str, series: pd.Series) -> bool:
    """Detect ID/code columns that look numeric but are identifiers."""
    lower = col_name.lower()
    id_tokens = ["id", "code", "zip", "postal", "phone", "fax", "sku", "barcode"]
    if any(t in lower for t in id_tokens):
        return True
    coerced = _coerce_numeric_series(series).dropna()
    if coerced.empty:
        return False
    if coerced.nunique() == len(coerced) and coerced.min() >= 0:
        if (coerced == coerced.astype(int)).all():
            return True
    return False


def _is_metadata_like_column(col_name: str) -> bool:
    lower = col_name.lower()
    ignored_tokens = [
        "footnote",
        "note",
        "comment",
        "remark",
        "flag",
        "status",
        "sample_error",
        "sampling_error",
        "relative_sampling",
    ]
    return any(token in lower for token in ignored_tokens)


def _is_meaningful_numeric_column(
    series: pd.Series, col_name: str, df: pd.DataFrame
) -> bool:
    """True if column is a genuine metric: numeric, non-constant, non-ID, non-metadata."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return False
    if _is_metadata_like_column(col_name):
        return False
    if _is_id_like_column(col_name, series):
        return False
    coerced = _coerce_numeric_series(series).dropna()
    if coerced.empty or coerced.nunique() < 2:
        return False
    if coerced.std(ddof=0) == 0:
        return False
    return True


def compute_data_quality_score(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Produce a comprehensive data quality report with a 0–100 score and star rating.

    Dimensions scored:
      - Completeness  (missing value rate)
      - Uniqueness    (duplicate row rate)
      - Outlier ratio (IQR-fenced outliers across numeric cols)
      - Consistency   (zero-variance / all-null columns)
      - Skewness load (average absolute skew across numeric cols)

    Returns a dict with score, star_rating, breakdown, and narrative badge.
    """
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = int(df.isnull().sum().sum())
    missing_pct = round(missing_cells / max(total_cells, 1) * 100, 2)

    dup_rows = int(df.duplicated().sum())
    dup_pct = round(dup_rows / max(len(df), 1) * 100, 2)

    numeric_cols = get_numeric_columns(df)
    outlier_counts = []
    skew_vals = []
    for col in numeric_cols:
        s = _coerce_numeric_series(df[col]).dropna()
        if len(s) < 4:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        if iqr > 0:
            n_out = int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())
            outlier_counts.append(n_out / len(s) * 100)
        skew_vals.append(abs(float(s.skew())))

    outlier_pct = round(float(np.mean(outlier_counts)) if outlier_counts else 0.0, 2)
    avg_skew = round(float(np.mean(skew_vals)) if skew_vals else 0.0, 2)

    bad_cols = sum(
        1 for col in df.columns if df[col].isnull().all() or df[col].nunique() <= 1
    )
    consistency_pct = round(bad_cols / max(df.shape[1], 1) * 100, 2)

    completeness_score = max(0.0, 100 - missing_pct * 2)
    uniqueness_score = max(0.0, 100 - dup_pct * 3)
    outlier_score = max(0.0, 100 - outlier_pct * 2)
    consistency_score = max(0.0, 100 - consistency_pct * 5)
    skew_score = max(0.0, 100 - min(avg_skew * 15, 100))

    final_score = round(
        completeness_score * 0.30
        + uniqueness_score * 0.25
        + outlier_score * 0.20
        + consistency_score * 0.15
        + skew_score * 0.10,
        1,
    )

    stars = (
        5
        if final_score >= 90
        else (
            4
            if final_score >= 75
            else 3 if final_score >= 60 else 2 if final_score >= 40 else 1
        )
    )
    star_str = "⭐" * stars + "☆" * (5 - stars)

    if final_score >= 90:
        badge = "Excellent"
    elif final_score >= 75:
        badge = "Good"
    elif final_score >= 60:
        badge = "Fair"
    elif final_score >= 40:
        badge = "Poor"
    else:
        badge = "Critical"

    return {
        "score": final_score,
        "stars": stars,
        "star_str": star_str,
        "badge": badge,
        "missing_pct": missing_pct,
        "duplicate_pct": dup_pct,
        "outlier_pct": outlier_pct,
        "avg_skewness": avg_skew,
        "consistency_score": consistency_score,
        "breakdown": {
            "completeness": round(completeness_score, 1),
            "uniqueness": round(uniqueness_score, 1),
            "outlier": round(outlier_score, 1),
            "consistency": round(consistency_score, 1),
            "skewness": round(skew_score, 1),
        },
        "raw": {
            "total_rows": len(df),
            "total_cols": df.shape[1],
            "missing_cells": missing_cells,
            "duplicate_rows": dup_rows,
            "bad_columns": bad_cols,
        },
    }


def detect_long_format(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect if the dataframe is in long format (one row per metric observation)."""
    result = {
        "is_long": False,
        "variable_col": None,
        "value_col": None,
        "time_col": None,
        "unit_col": None,
        "category_col": None,
    }

    value_candidates = []
    variable_candidates = []
    unit_candidates = []
    time_candidates = []
    category_candidates = []

    for col in df.columns:
        lower = col.lower()
        series = df[col]

        is_value_name = any(
            tok in lower
            for tok in [
                "value",
                "amount",
                "rd_value",
                "measure",
                "observation",
                "expenditure",
                "revenue",
                "sales",
                "income",
                "cost",
                "price",
            ]
        )
        if is_value_name or lower == "rd_value":
            coerced = _coerce_numeric_series(series).dropna()
            valid_ratio = len(coerced) / max(len(series.dropna()), 1)
            if valid_ratio >= 0.3:
                value_candidates.append(col)

        if series.dtype == object and 5 <= series.nunique() <= 300:
            if any(
                tok in lower
                for tok in ["variable", "metric", "indicator", "measure", "series"]
            ):
                variable_candidates.append(col)

        if any(tok in lower for tok in ["unit", "units", "currency", "denomination"]):
            if series.dtype == object and 1 <= series.nunique() <= 30:
                unit_candidates.append(col)

        if any(
            tok in lower
            for tok in ["year", "date", "month", "quarter", "period", "time", "week"]
        ):
            if series.nunique() >= 2:
                time_candidates.append(col)

        if any(
            tok in lower
            for tok in [
                "category",
                "breakdown",
                "group",
                "class",
                "sector",
                "industry",
                "region",
                "department",
                "type",
                "level",
                "variant",
                "segment",
            ]
        ):
            if series.dtype == object and 2 <= series.nunique() <= 200:
                category_candidates.append(col)

    if value_candidates and (variable_candidates or unit_candidates):
        result["is_long"] = True
        result["value_col"] = value_candidates[0]
        result["variable_col"] = variable_candidates[0] if variable_candidates else None
        result["unit_col"] = unit_candidates[0] if unit_candidates else None
        result["time_col"] = time_candidates[0] if time_candidates else None
        result["category_col"] = category_candidates[0] if category_candidates else None

    return result


def pivot_long_to_wide(
    df: pd.DataFrame,
    long_info: Dict[str, Any],
    unit_filter: Optional[str] = None,
) -> Tuple[pd.DataFrame, str]:
    """Convert long-format dataframe to wide format. Returns (wide_df, active_unit_label)."""
    value_col = long_info["value_col"]
    variable_col = long_info["variable_col"]
    unit_col = long_info["unit_col"]
    time_col = long_info["time_col"]

    working = df.copy()

    active_unit = ""
    if unit_col and unit_col in working.columns:
        units = working[unit_col].dropna().unique()
        if len(units) > 1:
            if unit_filter and unit_filter in units:
                working = working[working[unit_col] == unit_filter]
                active_unit = unit_filter
            else:
                dominant = working[unit_col].value_counts().idxmax()
                working = working[working[unit_col] == dominant]
                active_unit = str(dominant)
        elif len(units) == 1:
            active_unit = str(units[0])

    if (
        variable_col
        and variable_col in working.columns
        and time_col
        and time_col in working.columns
    ):
        working[value_col] = _coerce_numeric_series(working[value_col])
        try:
            wide = working.pivot_table(
                index=time_col,
                columns=variable_col,
                values=value_col,
                aggfunc="mean",
            ).reset_index()
            wide.columns.name = None
            metric_cols = [c for c in wide.columns if c != time_col]
            if len(metric_cols) > 20:
                variances = {c: wide[c].var() for c in metric_cols}
                top20 = sorted(variances, key=variances.get, reverse=True)[:20]
                wide = wide[[time_col] + top20]
            return wide, active_unit
        except Exception:
            pass

    working[value_col] = _coerce_numeric_series(working[value_col])
    return working, active_unit


def detect_unit_column(df: pd.DataFrame) -> Optional[str]:
    for col in df.columns:
        lower = col.lower()
        if any(t in lower for t in ["unit", "units", "measure", "denomination"]):
            if df[col].dtype == object and 1 <= df[col].nunique() <= 30:
                return col
    return None


def detect_mixed_units(df: pd.DataFrame, metric_col: str) -> bool:
    """EC-04: detect fundamentally incompatible unit types in the same value column."""
    unit_col = detect_unit_column(df)
    if unit_col is None:
        return False
    units = df[unit_col].dropna().unique()
    if len(units) <= 1:
        return False
    unit_strings = [str(u).lower() for u in units]
    has_currency = any(
        any(
            t in u
            for t in [
                "dollar",
                "usd",
                "gbp",
                "eur",
                "nzd",
                "$",
                "million",
                "billion",
                "euro",
            ]
        )
        for u in unit_strings
    )
    has_percentage = any(
        "percent" in u or "%" in u or "ratio" in u or "gdp" in u for u in unit_strings
    )
    has_count = any(
        any(
            t in u
            for t in [
                "number",
                "count",
                "headcount",
                "employee",
                "enterprise",
                "business",
            ]
        )
        for u in unit_strings
    )
    return sum([has_currency, has_percentage, has_count]) >= 2


def get_dominant_unit_slice(
    df: pd.DataFrame, metric_col: str
) -> Tuple[pd.DataFrame, str]:
    unit_col = detect_unit_column(df)
    if unit_col is None:
        return df, ""
    dominant = df[unit_col].value_counts().idxmax()
    return df[df[unit_col] == dominant].copy(), str(dominant)


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Return columns that are genuine numeric metrics (not IDs, not metadata, not constant)."""
    result = []
    for col in df.columns:
        series = df[col]
        if pd.api.types.is_datetime64_any_dtype(series):
            continue
        if _is_metadata_like_column(col):
            continue
        if _is_id_like_column(col, series):
            continue
        if pd.api.types.is_numeric_dtype(series):
            if _is_meaningful_numeric_column(series, col, df):
                result.append(col)
            continue
        coerced = _coerce_numeric_series(series)
        valid_ratio = coerced.notna().sum() / max(len(series.dropna()), 1)
        if valid_ratio >= 0.5 and _is_meaningful_numeric_column(series, col, df):
            result.append(col)
    return result


def get_meaningful_numeric_columns(df: pd.DataFrame) -> List[str]:
    return get_numeric_columns(df)


def detect_temporal_column(
    df: pd.DataFrame, exclude: Optional[str] = None
) -> Optional[str]:
    """
    Find the best temporal column by data profiling, not just name.

    BUG FIX — Year integer epoch problem:
      Integer columns whose values are in the calendar-year range (1900–2100) are
      recognised as temporal WITHOUT being passed through pd.to_datetime().
      Passing them through to_datetime() interprets the integers as nanoseconds
      since the Unix epoch (1970-01-01), producing nonsense labels like
      "1970-01-01 00:00:00.0000002016".  We keep them as plain integers and let
      the visualization layer format them as year labels directly.
    """
    candidates = []
    for col in df.columns:
        if col == exclude:
            continue
        series = df[col]
        lower = col.lower()

        if pd.api.types.is_datetime64_any_dtype(series):
            candidates.append((col, 100, series.nunique()))
            continue

        if any(t in lower for t in ["date", "datetime", "timestamp"]):

            sample_vals = series.dropna().astype(str).head(20)
            looks_like_date_string = (
                sample_vals.str.match(r"^\d{4}[-/]\d{1,2}([-/]\d{1,2})?").sum() >= 2
            )
            if looks_like_date_string:
                parsed = pd.to_datetime(series, errors="coerce")
                if parsed.notna().sum() >= 2:
                    candidates.append((col, 90, parsed.nunique()))
                    continue

        if pd.api.types.is_numeric_dtype(series):
            coerced = pd.to_numeric(series, errors="coerce").dropna()
            if not coerced.empty:

                if any(
                    t in lower
                    for t in ["year", "month", "quarter", "week", "day", "period"]
                ):
                    if coerced.nunique() >= 2:
                        candidates.append((col, 85, coerced.nunique()))
                        continue
                in_year_range = ((coerced >= 1900) & (coerced <= 2100)).all()
                if in_year_range and coerced.nunique() >= 2:
                    candidates.append((col, 70, coerced.nunique()))
                    continue

        if series.dtype == object:
            if any(t in lower for t in ["year", "month", "quarter", "period", "time"]):
                if series.nunique() >= 2:
                    candidates.append((col, 60, series.nunique()))
                    continue
            sample = series.dropna().astype(str).head(20)
            fiscal_q = sample.str.match(r"^\d{4}[-_]?Q[1-4]$", case=False)
            yearmonth = sample.str.match(r"^\d{4}[-/]\d{1,2}$")
            if fiscal_q.sum() >= 2 or yearmonth.sum() >= 2:
                if series.nunique() >= 2:
                    candidates.append((col, 65, series.nunique()))
                    continue

    if not candidates:
        return None
    candidates.sort(key=lambda x: (-x[1], x[2]))
    return candidates[0][0]


def detect_ordered_categorical(df: pd.DataFrame, col: str) -> bool:
    """EC-11: Detect if a categorical column has ordered sequential values like Phase_1/Phase_2."""
    if col not in df.columns:
        return False
    series = df[col].dropna().astype(str)
    unique_vals = sorted(series.unique())
    if len(unique_vals) < 2:
        return False

    numbers = []
    for val in unique_vals:
        nums = re.findall(r"\d+", val)
        if nums:
            numbers.append(int(nums[-1]))

    if len(numbers) == len(unique_vals) and numbers == sorted(numbers):
        return True

    ordered_sets = [
        {"q1", "q2", "q3", "q4"},
        {
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        },
        {
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        },
        {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"},
        {"low", "medium", "high"},
        {"small", "medium", "large"},
        {"control", "treatment"},
    ]
    lower_vals = {v.lower() for v in unique_vals}
    for ordered_set in ordered_sets:
        if lower_vals.issubset(ordered_set) and len(lower_vals) >= 2:
            return True

    return False


def _test_normality_robust(series: pd.Series) -> bool:
    """
    Returns True if the data is likely normal, False if non-normal / skewed.

    Strategy (no Shapiro above 5 000 observations):
      n < 50   → Shapiro-Wilk (still valid for small n)
      50–5000  → D'Agostino-Pearson (omnibus skew+kurtosis)
      >5000    → Jarque-Bera + abs(skew) < 0.5 heuristic
    The function returns True only if all applicable tests agree it is normal.
    """
    clean = series.dropna()
    n = len(clean)
    if n < 8:
        return True

    skewness = float(clean.skew())
    kurt = float(clean.kurtosis())

    if n < 50:
        try:
            _, p = scipy_stats.shapiro(clean)
            return p >= 0.05
        except Exception:
            return abs(skewness) < 0.5

    if n <= 5000:
        try:
            _, p = scipy_stats.normaltest(clean)
            return p >= 0.05
        except Exception:
            return abs(skewness) < 0.5
    try:
        _, p_jb = scipy_stats.jarque_bera(clean)
        is_normal_jb = p_jb >= 0.05
    except Exception:
        is_normal_jb = True

    is_normal_skew = abs(skewness) < 0.5
    is_normal_kurt = abs(kurt) < 3.0
    try:
        result = scipy_stats.anderson(clean.sample(min(n, 10_000), random_state=42))

        is_normal_ad = result.statistic < result.critical_values[2]
    except Exception:
        is_normal_ad = True

    votes = [is_normal_jb, is_normal_skew, is_normal_kurt, is_normal_ad]
    return sum(votes) >= 3


def _choose_correlation_method(series: pd.Series) -> str:
    """
    Automatically select the appropriate correlation method per column.
    Uses the robust normality test (Issue 1 fix).
      - Pearson  → continuous, approximately normal
      - Spearman → non-normal or skewed
      - Kendall  → small datasets (n < 30)
    """
    clean = series.dropna()
    n = len(clean)
    if n < 30:
        return "kendall"
    if not _test_normality_robust(clean):
        return "spearman"
    return "pearson"


def _dominant_correlation_method(df: pd.DataFrame, numeric_cols: List[str]) -> str:
    """
    Pick a single correlation method for the whole matrix by majority vote.
    Conservative hierarchy: kendall > spearman > pearson.
    """
    methods = [
        _choose_correlation_method(_coerce_numeric_series(df[c])) for c in numeric_cols
    ]
    if "kendall" in methods:
        return "kendall"
    if "spearman" in methods:
        return "spearman"
    return "pearson"


def _score_metric_column(df: pd.DataFrame, col: str, time_col: Optional[str]) -> float:
    """
    Score a candidate metric column. Higher = better primary metric.
    Combines:
      - keyword bonus (revenue/sales/profit → strong domain signal)
      - coefficient of variation (relative dispersion, scale-invariant)
      - non-null ratio (prefer complete columns)
      - correlation with time (prefer columns that change over time)
    """
    s = _coerce_numeric_series(df[col]).dropna()
    if s.empty:
        return -1.0

    lower = col.lower()
    keyword_bonus = 0.0
    high_value_keywords = [
        "revenue",
        "sales",
        "profit",
        "income",
        "gdp",
        "total",
        "net",
        "gross",
    ]
    medium_value_keywords = [
        "value",
        "amount",
        "expenditure",
        "price",
        "cost",
        "close",
        "score",
    ]
    if any(k in lower for k in high_value_keywords):
        keyword_bonus = 30.0
    elif any(k in lower for k in medium_value_keywords):
        keyword_bonus = 15.0

    mean_val = float(s.mean())
    std_val = float(s.std(ddof=0))
    cv = (std_val / abs(mean_val)) if abs(mean_val) > 1e-9 else std_val
    cv_score = min(cv * 20, 40.0)

    null_ratio = s.size / max(len(df), 1)
    completeness_score = null_ratio * 20.0

    time_corr_score = 0.0
    if time_col and time_col in df.columns:
        t_series = _coerce_numeric_series(df[time_col])
        overlap = s.index.intersection(t_series.dropna().index)
        if len(overlap) >= 4:
            try:
                corr = abs(float(s.loc[overlap].corr(t_series.loc[overlap])))
                if not np.isnan(corr):
                    time_corr_score = corr * 10.0
            except Exception:
                pass

    return keyword_bonus + cv_score + completeness_score + time_corr_score


def _choose_primary_metric(
    df: pd.DataFrame,
    metric_cols: List[str],
    time_col: Optional[str],
) -> Optional[str]:
    """Score-based primary metric selection — skips binary/near-binary columns."""
    if not metric_cols:
        return None
    candidates = [c for c in metric_cols if c != time_col]
    if not candidates:
        return None
    non_binary = []
    for c in candidates:
        s = _coerce_numeric_series(df[c]).dropna()
        if s.nunique() <= 2 and (s.max() - s.min()) <= 1:
            continue
        non_binary.append(c)

    filtered = non_binary if non_binary else candidates

    scores = {c: _score_metric_column(df, c, time_col) for c in filtered}
    return max(scores, key=scores.get)


def build_chart_plan(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Master chart planning function implementing all 14 edge cases.
    Returns a complete chart plan dict.
    """
    numeric_cols = get_numeric_columns(df)
    n_numeric = len(numeric_cols)

    long_info = detect_long_format(df)
    time_col = detect_temporal_column(df)
    unit_col = detect_unit_column(df)
    mixed_units = False
    active_unit = ""

    analysis_df = df.copy()
    metric_cols = numeric_cols.copy()

    if long_info["is_long"]:
        if long_info["unit_col"]:
            mixed_units = detect_mixed_units(df, long_info["value_col"])
        analysis_df, active_unit = pivot_long_to_wide(df, long_info)
        numeric_cols = get_numeric_columns(analysis_df)
        n_numeric = len(numeric_cols)
        time_col = detect_temporal_column(analysis_df)
        metric_cols = [c for c in numeric_cols if c != time_col]
    else:
        if unit_col:
            value_col = _find_value_col(df)
            if value_col:
                mixed_units = detect_mixed_units(df, value_col)
                if mixed_units:
                    analysis_df, active_unit = get_dominant_unit_slice(df, value_col)
                    numeric_cols = get_numeric_columns(analysis_df)
                    n_numeric = len(numeric_cols)
                    metric_cols = numeric_cols.copy()

    primary_metric = _choose_primary_metric(analysis_df, metric_cols, time_col)
    categorical_col = _find_categorical_col(analysis_df, primary_metric, time_col)
    feature_col = (
        time_col if time_col else _find_feature_col(analysis_df, primary_metric)
    )

    corr_method = (
        _dominant_correlation_method(analysis_df, metric_cols)
        if metric_cols
        else "pearson"
    )

    if n_numeric == 0 or primary_metric is None:
        return _no_charts_plan(analysis_df, active_unit)

    if n_numeric == 1 and not time_col and not categorical_col:
        return _no_charts_plan(analysis_df, active_unit)

    all_constant = all(
        analysis_df[c].nunique() < 2 for c in metric_cols if c in analysis_df.columns
    )
    if all_constant:
        return _no_charts_plan(analysis_df, active_unit)

    if mixed_units and not active_unit:
        return _no_charts_plan(analysis_df, active_unit)

    has_multi_metrics = len(metric_cols) >= 2
    has_time = (
        time_col is not None
        and time_col in analysis_df.columns
        and analysis_df[time_col].nunique() >= 2
    )
    has_categorical = (
        categorical_col is not None
        and categorical_col in analysis_df.columns
        and analysis_df[categorical_col].nunique() >= 2
    )
    is_ordered_cat = (
        detect_ordered_categorical(analysis_df, categorical_col)
        if categorical_col
        else False
    )

    gen_heatmap = False
    gen_trend = False
    gen_bar = False
    trend_x = None
    bar_x = None

    if has_multi_metrics and not has_time and not has_categorical:
        gen_heatmap = True

    elif has_time and not has_multi_metrics and not has_categorical:
        gen_trend = True
        trend_x = time_col

    elif has_time and has_multi_metrics and not has_categorical:
        gen_heatmap = True
        gen_trend = True
        trend_x = time_col

    elif has_categorical and not has_time and not has_multi_metrics:
        gen_bar = True
        bar_x = categorical_col

    elif has_time and has_categorical and has_multi_metrics:
        gen_heatmap = True
        gen_trend = True
        gen_bar = True
        trend_x = time_col
        bar_x = categorical_col

    elif is_ordered_cat and has_multi_metrics and not has_time:
        gen_heatmap = True
        gen_trend = True
        gen_bar = True
        trend_x = categorical_col
        bar_x = categorical_col

    elif has_time and has_multi_metrics:
        gen_heatmap = True
        gen_trend = True
        if analysis_df[time_col].nunique() <= 20:
            gen_bar = True
            bar_x = time_col
        trend_x = time_col

    elif has_time and has_categorical and not has_multi_metrics:
        time_unique = analysis_df[time_col].nunique()
        if time_unique >= 2:
            gen_trend = True
            trend_x = time_col
        gen_bar = True
        bar_x = categorical_col

    elif has_categorical:
        gen_bar = True
        bar_x = categorical_col

    elif has_time:
        gen_trend = True
        trend_x = time_col

    return {
        "analysis_df": analysis_df,
        "active_unit": active_unit,
        "primary_metric": primary_metric,
        "metric_cols": metric_cols,
        "time_col": time_col,
        "categorical_col": categorical_col,
        "feature_col": feature_col,
        "generate_heatmap": gen_heatmap,
        "generate_trend": gen_trend,
        "generate_bar": gen_bar,
        "trend_x": trend_x,
        "bar_x": bar_x,
        "is_long_format": long_info["is_long"],
        "mixed_units_detected": mixed_units,
        "correlation_method": corr_method,
    }


def _no_charts_plan(df: pd.DataFrame, active_unit: str = "") -> Dict[str, Any]:
    return {
        "analysis_df": df,
        "active_unit": active_unit,
        "primary_metric": None,
        "metric_cols": [],
        "time_col": None,
        "categorical_col": None,
        "feature_col": None,
        "generate_heatmap": False,
        "generate_trend": False,
        "generate_bar": False,
        "trend_x": None,
        "bar_x": None,
        "is_long_format": False,
        "mixed_units_detected": False,
        "correlation_method": "pearson",
    }


def _find_value_col(df: pd.DataFrame) -> Optional[str]:
    for col in df.columns:
        lower = col.lower()
        if any(t in lower for t in ["value", "amount", "rd_value", "measure"]):
            coerced = _coerce_numeric_series(df[col]).dropna()
            if len(coerced) / max(len(df), 1) >= 0.4:
                return col
    return None


def _find_categorical_col(
    df: pd.DataFrame,
    metric_col: Optional[str],
    time_col: Optional[str],
) -> Optional[str]:
    candidates = []
    for col in df.columns:
        if col in (metric_col, time_col):
            continue
        if _is_metadata_like_column(col):
            continue
        series = df[col]
        if series.dtype == object or str(series.dtype) == "category":
            n_unique = series.nunique()
            if 2 <= n_unique <= 200:
                candidates.append((col, n_unique, "text"))
        elif pd.api.types.is_numeric_dtype(series):
            n_unique = series.nunique()

            lower = col.lower()
            is_ordinal_like = any(
                t in lower
                for t in [
                    "day_of_week",
                    "day_of_month",
                    "day_of_year",
                    "week",
                    "hour",
                    "minute",
                    "second",
                    "month",
                    "quarter",
                    "year",
                ]
            )
            if is_ordinal_like:
                continue
            if 2 <= n_unique <= 20:
                candidates.append((col, n_unique, "numeric"))

    if not candidates:
        return None

    text_cats = [(c, n) for c, n, t in candidates if t == "text"]
    num_cats = [(c, n) for c, n, t in candidates if t == "numeric"]

    if text_cats:
        text_cats.sort(key=lambda x: x[1])
        return text_cats[0][0]
    num_cats.sort(key=lambda x: x[1])
    return num_cats[0][0] if num_cats else None


def _find_feature_col(
    df: pd.DataFrame,
    metric_col: Optional[str],
) -> Optional[str]:
    numeric_cols = get_numeric_columns(df)
    useful = [c for c in numeric_cols if c != metric_col and df[c].nunique() > 1]
    return useful[0] if useful else None


def compute_descriptive_stats(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    numeric_columns = get_numeric_columns(df)
    stats_dict = {}
    for col in numeric_columns:
        numeric_series = _coerce_numeric_series(df[col]).dropna()
        if numeric_series.empty or numeric_series.nunique() < 2:
            continue
        stats_dict[col] = {
            "mean": float(numeric_series.mean()),
            "median": float(numeric_series.median()),
            "std_dev": float(numeric_series.std()) if len(numeric_series) > 1 else 0.0,
            "min_value": float(numeric_series.min()),
            "max_value": float(numeric_series.max()),
            "skewness": float(numeric_series.skew()),
            "kurtosis": float(numeric_series.kurtosis()),
        }
    return stats_dict


_MIN_OVERLAP = 20


def _pairwise_corr_with_overlap(
    df: pd.DataFrame,
    method: str = "pearson",
    min_overlap: int = _MIN_OVERLAP,
) -> pd.DataFrame:
    """
    Compute pairwise correlations only when columns share at least min_overlap
    common non-null rows.  Pairs that fail the overlap check are set to NaN
    (later filled to 0.0 in the public API so downstream code stays unchanged).
    """
    cols = list(df.columns)
    n = len(cols)
    mat = np.full((n, n), np.nan)
    np.fill_diagonal(mat, 1.0)

    for i in range(n):
        for j in range(i + 1, n):
            mask = df.iloc[:, i].notna() & df.iloc[:, j].notna()
            overlap = int(mask.sum())
            if overlap < min_overlap:

                continue
            a = df.iloc[:, i][mask]
            b = df.iloc[:, j][mask]
            try:
                if method == "kendall":
                    r, _ = scipy_stats.kendalltau(a, b)
                elif method == "spearman":
                    r, _ = scipy_stats.spearmanr(a, b)
                else:
                    r = float(a.corr(b))
                mat[i, j] = r
                mat[j, i] = r
            except Exception:
                pass

    return pd.DataFrame(mat, index=cols, columns=cols)


def generate_correlation_matrix(
    df: pd.DataFrame,
    method: str = "pearson",
) -> Dict[str, Dict[str, float]]:
    """
    Compute correlation matrix with minimum-overlap enforcement (Issue 4 fix).
    method: 'pearson' | 'spearman' | 'kendall'
    """
    numeric_columns = get_meaningful_numeric_columns(df)
    if len(numeric_columns) < 2:
        return {}

    numeric_df = pd.DataFrame(
        {col: _coerce_numeric_series(df[col]).astype(float) for col in numeric_columns}
    )
    if numeric_df.empty or len(numeric_df.columns) < 2:
        return {}

    numeric_df = numeric_df.loc[:, numeric_df.nunique() > 1]
    numeric_df = numeric_df.loc[:, numeric_df.std(ddof=0) > 0]
    if len(numeric_df.columns) < 2:
        return {}

    valid_methods = {"pearson", "spearman", "kendall"}
    use_method = method if method in valid_methods else "pearson"

    corr_df = _pairwise_corr_with_overlap(
        numeric_df, method=use_method, min_overlap=_MIN_OVERLAP
    )
    return corr_df.fillna(0.0).to_dict()


def extract_top_performers(
    df: pd.DataFrame, metric_col: str, top_n: int = 5
) -> pd.DataFrame:
    """Issue 6 fix: returns top performers only (used for backward compatibility)."""
    if metric_col not in df.columns:
        return pd.DataFrame()
    working = df.copy()
    working[metric_col] = _coerce_numeric_series(working[metric_col])
    return (
        working.dropna(subset=[metric_col])
        .sort_values(by=metric_col, ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def extract_performer_analysis(
    df: pd.DataFrame, metric_col: str, top_n: int = 5
) -> Dict[str, Any]:
    """
    Issue 6 fix — comprehensive performer analysis:
      - top performers (highest values)
      - bottom performers (lowest values)
      - percentile ranks for all rows
      - top growth (if a time/sequence column is present)
    """
    if metric_col not in df.columns:
        return {"top": [], "bottom": [], "growth": [], "percentile_col": None}

    working = df.copy()
    working[metric_col] = _coerce_numeric_series(working[metric_col])
    working = working.dropna(subset=[metric_col]).reset_index(drop=True)

    if working.empty:
        return {"top": [], "bottom": [], "growth": [], "percentile_col": None}

    pct_col = f"{metric_col}_pct_rank"
    working[pct_col] = working[metric_col].rank(pct=True).round(4) * 100

    top_df = working.sort_values(metric_col, ascending=False).head(top_n)
    bottom_df = working.sort_values(metric_col, ascending=True).head(top_n)

    growth_records: List[Dict] = []
    time_col = detect_temporal_column(working, exclude=metric_col)
    if time_col and time_col in working.columns:
        sorted_w = working.sort_values(time_col).copy()
        sorted_w["_growth"] = sorted_w[metric_col].pct_change() * 100
        growth_df = (
            sorted_w.dropna(subset=["_growth"])
            .sort_values("_growth", ascending=False)
            .head(top_n)
        )
        growth_records = growth_df.drop(columns=["_growth"]).to_dict(orient="records")

    return {
        "top": top_df.to_dict(orient="records"),
        "bottom": bottom_df.to_dict(orient="records"),
        "growth": growth_records,
        "percentile_col": pct_col,
    }
