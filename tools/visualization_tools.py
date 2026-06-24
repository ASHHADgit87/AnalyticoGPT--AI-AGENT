import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def generate_correlation_heatmap(
    matrix_data: dict, output_dir: str = "outputs/charts"
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    df_corr = pd.DataFrame(matrix_data)

    plt.figure(figsize=(6, 4))
    sns.set_theme(style="dark")
    plt.gcf().patch.set_facecolor("#08090f")

    ax = sns.heatmap(
        df_corr, annot=True, cmap="Purples", cbar=False, annot_kws={"size": 10}
    )
    ax.set_facecolor("#08090f")
    plt.xticks(color="#f3f4f6")
    plt.yticks(color="#f3f4f6")

    target_file = os.path.join(output_dir, "correlation_matrix.png")
    plt.savefig(target_file, dpi=200, bbox_inches="tight", facecolor="#08090f")
    plt.close()
    return target_file


def generate_trend_line_chart(
    df: pd.DataFrame, x_col: str, y_col: str, output_dir: str = "outputs/charts"
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(7, 4))
    plt.gcf().patch.set_facecolor("#08090f")
    ax = plt.axes()
    ax.set_facecolor("#0d0e15")

    sorted_df = df.sort_values(by=x_col)
    plt.plot(
        sorted_df[x_col],
        sorted_df[y_col],
        color="#a855f7",
        marker="o",
        linewidth=2,
        markersize=6,
    )

    ax.tick_params(colors="#f3f4f6")
    ax.xaxis.label.set_color("#f3f4f6")
    ax.yaxis.label.set_color("#f3f4f6")
    plt.xlabel(x_col)
    plt.ylabel(y_col)

    target_file = os.path.join(output_dir, f"{x_col}_vs_{y_col}_trend.png")
    plt.savefig(target_file, dpi=200, bbox_inches="tight", facecolor="#08090f")
    plt.close()
    return target_file
