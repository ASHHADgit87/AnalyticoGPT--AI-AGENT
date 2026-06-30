import os
import re
import textwrap
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
import scipy.stats as scipy_stats


def _coerce_numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace(r"[^0-9.\-]", "", regex=True)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def _clip_outliers(series: pd.Series) -> pd.Series:
    q_low = series.quantile(0.01)
    q_high = series.quantile(0.99)
    if q_low < q_high:
        return series.clip(lower=q_low, upper=q_high)
    return series


def _wrap_labels(labels: list, width: int = 14) -> list:
    return [textwrap.fill(str(lbl), width) for lbl in labels]


def generate_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    output_dir: str = "outputs/charts",
    unit_label: str = "",
    aggregation: str = "mean",
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    plot_df = df[[x_col, y_col]].copy()
    plot_df[y_col] = _coerce_numeric(plot_df[y_col])
    plot_df = plot_df.dropna(subset=[x_col, y_col])

    if plot_df.empty or len(plot_df) < 2:
        return ""

    if y_col != "__row_count__" and plot_df[y_col].nunique() < 2:
        return ""

    n_unique = plot_df[x_col].nunique()
    if n_unique > 20:
        top_cats = plot_df[x_col].value_counts().head(20).index
        plot_df = plot_df[plot_df[x_col].isin(top_cats)]

    if y_col == "__row_count__":
        plot_df = (
            plot_df.groupby(x_col, as_index=False)[y_col]
            .sum()
            .sort_values(by=y_col, ascending=False)
            .head(20)
        )
    else:
        agg_func = "median" if aggregation == "median" else "mean"
        plot_df = (
            plot_df.groupby(x_col, as_index=False)[y_col]
            .agg(agg_func)
            .sort_values(by=y_col, ascending=False)
            .head(20)
        )

    if plot_df.empty:
        return ""

    plot_df[y_col] = _clip_outliers(plot_df[y_col])

    if y_col != "__row_count__":
        y_range = plot_df[y_col].max() - plot_df[y_col].min()
        if y_range < 1e-6:
            return ""

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#08090f")
    ax.set_facecolor("#0d0e15")

    palette = ["#6366f1", "#a855f7", "#ec4899"]
    bar_colors = [palette[i % len(palette)] for i in range(len(plot_df))]
    x_labels = _wrap_labels(plot_df[x_col].astype(str).tolist())

    ax.bar(
        x_labels,
        plot_df[y_col],
        color=bar_colors,
        edgecolor="#1f293d",
        linewidth=0.5,
        alpha=0.88,
    )

    ax.tick_params(colors="#f3f4f6")
    ax.xaxis.label.set_color("#f3f4f6")
    ax.yaxis.label.set_color("#f3f4f6")
    ax.spines["bottom"].set_color("#1f293d")
    ax.spines["left"].set_color("#1f293d")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color="#1f293d", linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)

    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.xlabel(x_col, fontsize=10, color="#f3f4f6")
    if y_col == "__row_count__":
        display_y = "Count"
        agg_display = "Total"
    else:
        display_y = f"{y_col} ({unit_label})" if unit_label else y_col
        agg_display = "Median" if agg_func == "median" else "Mean"
    plt.ylabel(f"{agg_display} {display_y}", fontsize=10, color="#f3f4f6")
    title = f"{'Record Count' if y_col == '__row_count__' else y_col} by {x_col}"
    if unit_label:
        title += f"  [{unit_label}]"
    plt.title(title, color="#f3f4f6", fontsize=12, pad=10)

    def _sanitize(s: str) -> str:
        return re.sub(r'[\\/:*?"<>|]', "_", str(s))[:80]

    target_file = os.path.join(
        output_dir, f"{_sanitize(x_col)}_vs_{_sanitize(y_col)}_bar.png"
    )
    plt.savefig(target_file, dpi=200, bbox_inches="tight", facecolor="#08090f")
    plt.close()
    return target_file


_HEATMAP_MIN_ABS_R = 0.15


def generate_correlation_heatmap(
    matrix_data: dict,
    output_dir: str = "outputs/charts",
    method_label: str = "Pearson",
) -> str:
    if not matrix_data:
        return ""

    os.makedirs(output_dir, exist_ok=True)
    df_corr = pd.DataFrame(matrix_data)

    if df_corr.empty or df_corr.shape[0] < 2 or df_corr.shape[1] < 2:
        return ""

    non_diag = df_corr.values.copy().astype(float)
    np.fill_diagonal(non_diag, 0.0)

    if not np.any(non_diag != 0):
        return ""

    if np.nanmax(np.abs(non_diag)) < _HEATMAP_MIN_ABS_R:
        return ""

    n = df_corr.shape[0]
    fig_w = max(6, min(n * 0.9, 20))
    fig_h = max(4, min(n * 0.7, 16))
    plt.figure(figsize=(fig_w, fig_h))
    sns.set_theme(style="dark")
    plt.gcf().patch.set_facecolor("#08090f")

    short_cols = {c: "\n".join(textwrap.wrap(c, 16)) for c in df_corr.columns}
    df_corr = df_corr.rename(columns=short_cols, index=short_cols)

    annot_size = max(6, 9 - n // 4)

    corr_vals = df_corr.values.astype(float)

    normalized = (corr_vals + 1.0) / 2.0

    annot_array = np.array([[f"{v:.2f}" for v in row] for row in corr_vals])

    ax = sns.heatmap(
        df_corr,
        annot=annot_array,
        fmt="",
        cmap="magma",
        cbar=True,
        annot_kws={"size": annot_size},
        linewidths=0.5,
        linecolor="#1f293d",
        vmin=-1,
        vmax=1,
    )

    for i, text in enumerate(ax.texts):
        row = i // n
        col = i % n
        brightness = normalized[row, col]

        text.set_color("black" if brightness > 0.65 else "#f3f4f6")
        text.set_fontsize(annot_size)

    ax.set_facecolor("#08090f")
    tick_fs = max(6, 8 - n // 6)
    plt.xticks(color="#f3f4f6", rotation=45, ha="right", fontsize=tick_fs)
    plt.yticks(color="#f3f4f6", rotation=0, fontsize=tick_fs)
    plt.title(
        f"Correlation Matrix ({method_label})",
        color="#f3f4f6",
        fontsize=12,
        pad=10,
    )

    target_file = os.path.join(output_dir, "correlation_matrix.png")
    plt.savefig(target_file, dpi=200, bbox_inches="tight", facecolor="#08090f")
    plt.close()
    return target_file


def _compute_ols_confidence_band(
    x_numeric: np.ndarray,
    y_values: np.ndarray,
    alpha: float = 0.05,
) -> tuple:
    n = len(x_numeric)
    if n < 4:
        return None, None, None

    x = x_numeric.astype(float)
    y = y_values.astype(float)

    x_mean = np.mean(x)
    y_mean = np.mean(y)
    ss_xx = np.sum((x - x_mean) ** 2)
    if ss_xx == 0:
        return None, None, None

    b1 = np.sum((x - x_mean) * (y - y_mean)) / ss_xx
    b0 = y_mean - b1 * x_mean
    y_fit = b0 + b1 * x

    residuals = y - y_fit
    mse = np.sum(residuals**2) / max(n - 2, 1)
    s = np.sqrt(mse)
    se_fit = s * np.sqrt(1.0 / n + (x - x_mean) ** 2 / ss_xx)
    t_crit = scipy_stats.t.ppf(1 - alpha / 2, df=max(n - 2, 1))

    return y_fit, y_fit - t_crit * se_fit, y_fit + t_crit * se_fit


def generate_trend_line_chart(
    df: pd.DataFrame,
    x_col: Optional[str],
    y_col: str,
    output_dir: str = "outputs/charts",
    unit_label: str = "",
    show_confidence_interval: bool = True,
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    if x_col and x_col in df.columns:
        plot_df = df[[x_col, y_col]].copy()
    else:
        plot_df = df[[y_col]].copy().reset_index()
        x_col = "index"

    plot_df[y_col] = _coerce_numeric(plot_df[y_col])
    plot_df = plot_df.dropna(subset=[y_col])

    if plot_df.empty or plot_df[y_col].nunique() < 2:
        return ""

    if x_col in plot_df.columns and x_col != "index":

        x_series = plot_df[x_col]
        should_parse_datetime = False

        if pd.api.types.is_numeric_dtype(x_series):

            should_parse_datetime = False
        elif x_series.dtype == object:

            sample = x_series.dropna().astype(str).head(20)
            looks_like_date = (
                sample.str.match(r"^\d{4}[-/]\d{1,2}([-/]\d{1,2})?").sum() >= 2
            )
            should_parse_datetime = looks_like_date

        if should_parse_datetime:
            parsed = pd.to_datetime(plot_df[x_col], errors="coerce")
            if parsed.notna().sum() >= 2:
                plot_df[x_col] = parsed

        plot_df = plot_df.groupby(x_col, as_index=False)[y_col].mean()
        plot_df = plot_df.sort_values(by=x_col)

    if len(plot_df) < 2:
        return ""

    if len(plot_df) > 1000:
        step = max(1, len(plot_df) // 1000)
        plot_df = plot_df.iloc[::step]

    plot_df = plot_df.reset_index(drop=True)
    plot_df[y_col] = _clip_outliers(plot_df[y_col])

    x_values = list(range(len(plot_df)))

    raw_x = plot_df[x_col]
    if pd.api.types.is_datetime64_any_dtype(raw_x):
        x_labels = raw_x.dt.strftime("%Y-%m-%d").tolist()
    elif pd.api.types.is_numeric_dtype(raw_x):

        coerced = pd.to_numeric(raw_x, errors="coerce")
        if ((coerced >= 1900) & (coerced <= 2100)).all():
            x_labels = coerced.astype(int).astype(str).tolist()
        else:
            x_labels = [f"{v:.2f}" if v != int(v) else str(int(v)) for v in coerced]
    else:
        x_labels = raw_x.astype(str).tolist()

    y_values = np.array(plot_df[y_col].tolist(), dtype=float)

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#08090f")
    ax.set_facecolor("#0d0e15")

    marker = "o" if len(plot_df) <= 100 else None
    ax.plot(
        x_values, y_values, color="#a855f7", marker=marker, linewidth=2, markersize=5
    )
    ax.fill_between(x_values, y_values, alpha=0.08, color="#a855f7")

    if show_confidence_interval and len(y_values) >= 4:
        x_arr = np.array(x_values, dtype=float)
        y_fit, ci_lower, ci_upper = _compute_ols_confidence_band(x_arr, y_values)
        if y_fit is not None:
            ax.plot(
                x_values,
                y_fit,
                color="#f59e0b",
                linewidth=1.5,
                linestyle="--",
                label="OLS trend",
            )
            ax.fill_between(
                x_values,
                ci_lower,
                ci_upper,
                alpha=0.18,
                color="#f59e0b",
                label="95% OLS CI",
            )
            ax.legend(
                facecolor="#0d0e15",
                edgecolor="#1f293d",
                labelcolor="#f3f4f6",
                fontsize=8,
            )

    ax.tick_params(colors="#f3f4f6")
    ax.xaxis.label.set_color("#f3f4f6")
    ax.yaxis.label.set_color("#f3f4f6")
    ax.spines["bottom"].set_color("#1f293d")
    ax.spines["left"].set_color("#1f293d")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color="#1f293d", linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)

    plt.xlabel(x_col, fontsize=10, color="#f3f4f6")
    y_label = f"{y_col} ({unit_label})" if unit_label else y_col
    plt.ylabel(y_label, fontsize=10, color="#f3f4f6")
    title = f"{y_col} over {x_col}"
    if unit_label:
        title += f"  [{unit_label}]"
    plt.title(title, color="#f3f4f6", fontsize=12, pad=10)

    wrapped_labels = _wrap_labels(x_labels)
    if len(plot_df) > 12:
        step = max(1, len(plot_df) // 12)
        sampled = list(range(0, len(plot_df), step))[:12]
        if sampled[-1] != len(plot_df) - 1:
            sampled.append(len(plot_df) - 1)
        plt.xticks(
            sampled,
            [wrapped_labels[i] for i in sampled],
            rotation=45,
            ha="right",
            fontsize=8,
        )
    else:
        plt.xticks(
            list(range(len(plot_df))),
            wrapped_labels,
            rotation=45,
            ha="right",
            fontsize=8,
        )

    def _sanitize(s: str) -> str:
        return re.sub(r'[\\/:*?"<>|]', "_", str(s))[:80]

    target_file = os.path.join(
        output_dir, f"{_sanitize(x_col)}_vs_{_sanitize(y_col)}_trend.png"
    )
    plt.savefig(target_file, dpi=200, bbox_inches="tight", facecolor="#08090f")
    plt.close()
    return target_file
