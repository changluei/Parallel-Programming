from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path(r"E:\桌面\大二下\并行\作业2：cpu架构相关编程\CPU架构相关编程\fig")
OUTPUT_PDF = OUTPUT_DIR / "n_number_sum_profile_bar.pdf"

ALGORITHMS = ["平凡链式", "两路链式", "递归算法"]
COLORS = ["#897CD3", "#90BFCF", "#D8B27A"]
EDGE_COLORS = ["#5f54a3", "#5f8e9b", "#8e7145"]

METRICS = ["Instructions Retired", "Clockticks", "CPI Rate", "CPU Time (ms)"]

VALUES_LEFT = {
    "Instructions Retired": [42.0, 39.2, 112.0],
    "Clockticks": [36.4, 16.8, 19.6],
}

VALUES_RIGHT = {
    "CPI Rate": [0.867, 0.429, 0.175],
    "CPU Time (ms)": [7.991, 3.995, 6.992],
}


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def add_labels(ax, bars, values, offset, suffix=""):
    for bar, value in zip(bars, values):
        text = f"{value:.1f}{suffix}" if suffix else f"{value:.3f}"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + offset,
            text,
            ha="center",
            va="bottom",
            fontsize=9.0,
        )


def main() -> None:
    setup_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    x = np.arange(len(METRICS), dtype=float)
    width = 0.22
    offsets = np.array([-width, 0.0, width])

    fig, ax_left = plt.subplots(figsize=(10.2, 5.6))
    ax_right = ax_left.twinx()

    legend_handles = []
    left_metrics = METRICS[:2]
    right_metrics = METRICS[2:]

    for idx, algorithm in enumerate(ALGORITHMS):
        left_values = [VALUES_LEFT[m][idx] for m in left_metrics]
        bars = ax_left.bar(
            x[:2] + offsets[idx],
            left_values,
            width=width,
            color=COLORS[idx],
            edgecolor=EDGE_COLORS[idx],
            linewidth=1.0,
            zorder=3,
            label=algorithm,
        )
        add_labels(ax_left, bars, left_values, 2.0, "M")
        if idx == 0:
            legend_handles.append(bars[0])
        elif idx == 1:
            legend_handles.append(bars[0])
        else:
            legend_handles.append(bars[0])

    for idx, algorithm in enumerate(ALGORITHMS):
        right_values = [VALUES_RIGHT[m][idx] for m in right_metrics]
        bars = ax_right.bar(
            x[2:] + offsets[idx],
            right_values,
            width=width,
            color=COLORS[idx],
            edgecolor=EDGE_COLORS[idx],
            linewidth=1.0,
            zorder=3,
        )
        add_labels(ax_right, bars[:1], right_values[:1], 0.18)
        add_labels(ax_right, bars[1:], right_values[1:], 0.18)

    ax_left.set_xticks(x)
    ax_left.set_xticklabels(METRICS, fontsize=11)
    ax_left.set_xlabel("指标", fontsize=12)
    ax_left.set_ylabel("Instructions / Clockticks (Million)", fontsize=12)
    ax_right.set_ylabel("CPI / CPU Time (ms)", fontsize=12)

    ax_left.set_ylim(0, 125)
    ax_right.set_ylim(0, 9.5)

    ax_left.grid(True, axis="y", linestyle="--", linewidth=0.8, alpha=0.22, zorder=0)
    ax_right.grid(False)
    ax_left.set_axisbelow(True)

    ax_left.legend(
        legend_handles,
        ALGORITHMS,
        loc="upper left",
        frameon=True,
        framealpha=0.95,
        edgecolor="#d0d0d0",
        fontsize=10.5,
    )

    for spine in ax_left.spines.values():
        spine.set_linewidth(1.0)
    for spine in ax_right.spines.values():
        spine.set_linewidth(1.0)

    fig.tight_layout()
    fig.savefig(OUTPUT_PDF, bbox_inches="tight")
    print(f"Saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
