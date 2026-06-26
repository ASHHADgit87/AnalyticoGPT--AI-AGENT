import os
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
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

    plt.figure(figsize=(14, 6))
    plt.gcf().patch.set_facecolor("#08090f")
    ax = plt.axes()
    ax.set_facecolor("#0d0e15")

    plt.bar(plot_df[x_col].astype(str), plot_df[y_col], color="#60a5fa")
    ax.tick_params(colors="#f3f4f6")
    ax.xaxis.label.set_color("#f3f4f6")
    ax.yaxis.label.set_color("#f3f4f6")
    plt.xticks(rotation=45, ha="right")
    plt.xlabel(x_col)
    plt.ylabel(y_col)

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

    plt.figure(figsize=(6, 4))
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
    )
    ax.set_facecolor("#08090f")
    plt.xticks(color="#f3f4f6")
    plt.yticks(color="#f3f4f6")

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
    plot_df = plot_df.dropna(subset=[y_col, x_col])

    if x_col and x_col in plot_df.columns and x_col != "index":
        plot_df = (
            plot_df.groupby(x_col, as_index=False)[y_col].mean().sort_values(by=x_col)
        )
    else:
        plot_df = plot_df.sort_values(by=x_col)

    if len(plot_df) > 1000:
        step = max(1, len(plot_df) // 1000)
        plot_df = plot_df.iloc[::step]

    plot_df = plot_df.reset_index(drop=True)
    x_values = list(range(len(plot_df)))
    x_labels = plot_df[x_col].astype(str).tolist()
    y_values = plot_df[y_col].tolist()

    plt.figure(figsize=(14, 6))
    plt.gcf().patch.set_facecolor("#08090f")
    ax = plt.axes()
    ax.set_facecolor("#0d0e15")

    marker = "o" if len(plot_df) <= 1000 else None
    plt.plot(
        x_values,
        y_values,
        color="#a855f7",
        marker=marker,
        linewidth=2,
        markersize=6,
    )

    ax.tick_params(colors="#f3f4f6")
    ax.xaxis.label.set_color("#f3f4f6")
    ax.yaxis.label.set_color("#f3f4f6")
    plt.xlabel(x_col)
    plt.ylabel(y_col)

    if len(plot_df) > 12:
        step = max(1, len(plot_df) // 12)
        sampled_positions = list(range(0, len(plot_df), step))[:12]
        if sampled_positions[-1] != len(plot_df) - 1:
            sampled_positions.append(len(plot_df) - 1)
        plt.xticks(
            sampled_positions,
            [x_labels[position] for position in sampled_positions],
            rotation=45,
            ha="right",
        )
    else:
        plt.xticks(
            list(range(len(plot_df))),
            x_labels,
            rotation=45,
            ha="right",
        )

    target_file = os.path.join(output_dir, f"{x_col}_vs_{y_col}_trend.png")
    plt.savefig(target_file, dpi=200, bbox_inches="tight", facecolor="#08090f")
    plt.close()
    return target_file
