from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path(r"E:\桌面\大二下\并行\作业2：cpu架构相关编程\CPU架构相关编程\fig")
OUTPUT_PDF = OUTPUT_DIR / "matrix_cache_cpi_miss_bar.pdf"

NAIVE_VALUES = {
    "CPI": 4.511,
    "L1 miss rate": 43.7,
    "L2 miss rate": 92.3,
    "L3 miss rate": 85.8,
}

OPTIMIZED_VALUES = {
    "CPI": 0.544,
    "L1 miss rate": 11.2,
    "L2 miss rate": 13.4,
    "L3 miss rate": 97.8,
}

NAIVE_COLOR = "#897CD3"
OPTIMIZED_COLOR = "#90BFCF"


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
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + offset,
            f"{value:.1f}{suffix}" if suffix else f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=9.5,
        )


def main() -> None:
    setup_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metrics = list(NAIVE_VALUES.keys())
    x = np.arange(len(metrics), dtype=float)
    width = 0.34

    fig, ax_left = plt.subplots(figsize=(8.8, 5.3))
    ax_right = ax_left.twinx()

    cpi_x = np.array([x[0]])
    miss_x = x[1:]

    naive_cpi = np.array([NAIVE_VALUES["CPI"]], dtype=float)
    optimized_cpi = np.array([OPTIMIZED_VALUES["CPI"]], dtype=float)
    naive_rates = np.array([NAIVE_VALUES[m] for m in metrics[1:]], dtype=float)
    optimized_rates = np.array([OPTIMIZED_VALUES[m] for m in metrics[1:]], dtype=float)

    bars1_cpi = ax_left.bar(
        cpi_x - width / 2,
        naive_cpi,
        width=width,
        color=NAIVE_COLOR,
        edgecolor="#5f54a3",
        linewidth=1.0,
        label="平凡算法",
        zorder=3,
    )
    bars2_cpi = ax_left.bar(
        cpi_x + width / 2,
        optimized_cpi,
        width=width,
        color=OPTIMIZED_COLOR,
        edgecolor="#5f8e9b",
        linewidth=1.0,
        label="优化算法",
        zorder=3,
    )

    bars1_rate = ax_right.bar(
        miss_x - width / 2,
        naive_rates,
        width=width,
        color=NAIVE_COLOR,
        edgecolor="#5f54a3",
        linewidth=1.0,
        zorder=3,
    )
    bars2_rate = ax_right.bar(
        miss_x + width / 2,
        optimized_rates,
        width=width,
        color=OPTIMIZED_COLOR,
        edgecolor="#5f8e9b",
        linewidth=1.0,
        zorder=3,
    )

    ax_left.set_xticks(x)
    ax_left.set_xticklabels(metrics, fontsize=11)
    ax_left.set_xlabel("指标", fontsize=12)
    ax_left.set_ylabel("CPI", fontsize=12)
    ax_right.set_ylabel("Miss Rate (%)", fontsize=12)

    ax_left.set_ylim(0, 10)
    ax_right.set_ylim(0, 100)

    ax_left.grid(True, axis="y", linestyle="--", linewidth=0.8, alpha=0.22, zorder=0)
    ax_right.grid(False)
    ax_left.set_axisbelow(True)

    ax_left.legend(
        [bars1_cpi[0], bars2_cpi[0]],
        ["平凡算法", "优化算法"],
        loc="upper left",
        frameon=True,
        framealpha=0.95,
        edgecolor="#d0d0d0",
        fontsize=10.5,
    )

    add_labels(ax_left, bars1_cpi, naive_cpi, 0.18)
    add_labels(ax_left, bars2_cpi, optimized_cpi, 0.18)
    add_labels(ax_right, bars1_rate, naive_rates, 2.0, "%")
    add_labels(ax_right, bars2_rate, optimized_rates, 2.0, "%")

    for spine in ax_left.spines.values():
        spine.set_linewidth(1.0)
    for spine in ax_right.spines.values():
        spine.set_linewidth(1.0)

    fig.tight_layout()
    fig.savefig(OUTPUT_PDF, bbox_inches="tight")
    print(f"Saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
