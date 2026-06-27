import os
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def generate_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    output_dir: str = "outputs/charts",
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    plot_df = df[[x_col, y_col]].copy()
    plot_df = plot_df.dropna(subset=[x_col, y_col])
    plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors="coerce")
    plot_df = plot_df.dropna(subset=[y_col])

    if plot_df.empty:
        return ""

    if plot_df[x_col].nunique() > 20:
        plot_df = (
            plot_df.groupby(x_col, as_index=False)[y_col]
            .mean()
            .sort_values(by=y_col, ascending=False)
            .head(20)
        )
    else:
        plot_df = (
            plot_df.groupby(x_col, as_index=False)[y_col]
            .mean()
            .sort_values(by=y_col, ascending=False)
        )

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#08090f")
    ax.set_facecolor("#0d0e15")

    bars = ax.bar(
        plot_df[x_col].astype(str),
        plot_df[y_col],
        color="#a855f7",
        edgecolor="#6366f1",
        linewidth=0.5,
    )

    colors = ["#6366f1", "#a855f7", "#ec4899"]
    for idx, bar in enumerate(bars):
        bar.set_color(colors[idx % len(colors)])
        bar.set_alpha(0.85)

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
    plt.xlabel(x_col, fontsize=10)
    plt.ylabel(y_col, fontsize=10)
    plt.title(f"{y_col} by {x_col}", color="#f3f4f6", fontsize=12, pad=10)

    target_file = os.path.join(output_dir, f"{x_col}_vs_{y_col}_bar.png")
    plt.savefig(target_file, dpi=200, bbox_inches="tight", facecolor="#08090f")
    plt.close()
    return target_file


def generate_correlation_heatmap(
    matrix_data: dict, output_dir: str = "outputs/charts"
) -> str:

    if not matrix_data:
        return ""

    os.makedirs(output_dir, exist_ok=True)
    df_corr = pd.DataFrame(matrix_data)

    if df_corr.empty or df_corr.shape[0] < 3 or df_corr.shape[1] < 3:
        return ""

    non_diag = df_corr.values.copy()
    import numpy as np

    np.fill_diagonal(non_diag, 0)
    if not np.any(non_diag != 0):
        return ""

    n = df_corr.shape[0]
    fig_size = max(6, n * 0.8)
    plt.figure(figsize=(fig_size, fig_size * 0.7))
    sns.set_theme(style="dark")
    plt.gcf().patch.set_facecolor("#08090f")

    ax = sns.heatmap(
        df_corr,
        annot=True,
        cmap="magma",
        cbar=True,
        annot_kws={"size": 9, "color": "#f3f4f6"},
        linewidths=0.5,
        linecolor="#1f293d",
        vmin=-1,
        vmax=1,
        fmt=".2f",
    )
    ax.set_facecolor("#08090f")
    plt.xticks(color="#f3f4f6", rotation=45, ha="right", fontsize=8)
    plt.yticks(color="#f3f4f6", rotation=0, fontsize=8)
    plt.title("Correlation Matrix", color="#f3f4f6", fontsize=12, pad=10)

    target_file = os.path.join(output_dir, "correlation_matrix.png")
    plt.savefig(target_file, dpi=200, bbox_inches="tight", facecolor="#08090f")
    plt.close()
    return target_file


def generate_trend_line_chart(
    df: pd.DataFrame,
    x_col: Optional[str],
    y_col: str,
    output_dir: str = "outputs/charts",
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    if x_col and x_col in df.columns:
        plot_df = df[[x_col, y_col]].copy()
    else:
        plot_df = df[[y_col]].copy().reset_index()
        x_col = "index"

    plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors="coerce")
    plot_df = plot_df.dropna(subset=[y_col])

    if plot_df.empty:
        return ""

    if plot_df[y_col].nunique() < 2:
        return ""

    if x_col and x_col in plot_df.columns and x_col != "index":
        plot_df = (
            plot_df.groupby(x_col, as_index=False)[y_col].mean().sort_values(by=x_col)
        )
    else:
        plot_df = plot_df.sort_values(by=x_col)

    if len(plot_df) < 2:
        return ""

    if len(plot_df) > 1000:
        step = max(1, len(plot_df) // 1000)
        plot_df = plot_df.iloc[::step]

    plot_df = plot_df.reset_index(drop=True)
    x_values = list(range(len(plot_df)))
    x_labels = plot_df[x_col].astype(str).tolist()
    y_values = plot_df[y_col].tolist()

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#08090f")
    ax.set_facecolor("#0d0e15")

    marker = "o" if len(plot_df) <= 100 else None
    ax.plot(
        x_values, y_values, color="#a855f7", marker=marker, linewidth=2, markersize=5
    )
    ax.fill_between(x_values, y_values, alpha=0.08, color="#a855f7")

    ax.tick_params(colors="#f3f4f6")
    ax.xaxis.label.set_color("#f3f4f6")
    ax.yaxis.label.set_color("#f3f4f6")
    ax.spines["bottom"].set_color("#1f293d")
    ax.spines["left"].set_color("#1f293d")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color="#1f293d", linewidth=0.5, alpha=0.6)
    ax.set_axisbelow(True)

    plt.xlabel(x_col, fontsize=10)
    plt.ylabel(y_col, fontsize=10)
    plt.title(f"{y_col} over {x_col}", color="#f3f4f6", fontsize=12, pad=10)

    if len(plot_df) > 12:
        step = max(1, len(plot_df) // 12)
        sampled = list(range(0, len(plot_df), step))[:12]
        if sampled[-1] != len(plot_df) - 1:
            sampled.append(len(plot_df) - 1)
        plt.xticks(
            sampled, [x_labels[i] for i in sampled], rotation=45, ha="right", fontsize=8
        )
    else:
        plt.xticks(
            list(range(len(plot_df))), x_labels, rotation=45, ha="right", fontsize=8
        )

    target_file = os.path.join(output_dir, f"{x_col}_vs_{y_col}_trend.png")
    plt.savefig(target_file, dpi=200, bbox_inches="tight", facecolor="#08090f")
    plt.close()
    return target_file
