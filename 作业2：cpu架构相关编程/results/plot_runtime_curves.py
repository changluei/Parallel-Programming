from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import ConnectionPatch, Rectangle
from matplotlib.ticker import FuncFormatter, MaxNLocator


RESULTS_DIR = Path(r"E:\桌面\大二下\并行\作业2：cpu架构相关编程\results")
SUM_SERIES_DIR = RESULTS_DIR / "series_from_1024_doubling"
MATRIX_SERIES_DIR = RESULTS_DIR / "cache_5stage_pow2like_series"
OUTPUT_DIR = Path(r"E:\桌面\大二下\并行\作业2：cpu架构相关编程\CPU架构相关编程\fig")

SUM_SIZES = [1024, 2048, 4096, 8192, 16384]
MATRIX_SIZES = [256, 1024, 1536, 1792, 2048]

MATRIX_TICK_LABELS = [
    "256\n< L1",
    "1024\n< L2",
    "1536\n< L3",
    "1792\n≈ L3",
    "2048\n> L3",
]
SUM_TICK_LABELS = [rf"$2^{{{n.bit_length() - 1}}}$" for n in SUM_SIZES]

MATRIX_ALGORITHMS = [
    "naive_column_major",
    "cache_optimized_row_major",
]
SUM_ALGORITHMS = [
    "naive_chain",
    "two_way_chain",
    "pairwise_reduction",
]
ALGORITHM_LABELS = {
    "naive_column_major": "Naive Column Major",
    "cache_optimized_row_major": "Cache Optimized Row Major",
    "naive_chain": "Naive Chain",
    "two_way_chain": "Two-Way Chain",
    "pairwise_reduction": "Pairwise Reduction",
}
ALGORITHM_COLORS = {
    "naive_column_major": "#1f77b4",
    "cache_optimized_row_major": "#d62728",
    "naive_chain": "#1f77b4",
    "two_way_chain": "#d62728",
    "pairwise_reduction": "#2ca02c",
}
ALGORITHM_MARKERS = {
    "naive_column_major": "o",
    "cache_optimized_row_major": "s",
    "naive_chain": "o",
    "two_way_chain": "s",
    "pairwise_reduction": "^",
}

MATRIX_INSET_BOUNDS = [0.12, 0.22, 0.26, 0.28]
MATRIX_INSET_YMIN = 0.008
MATRIX_INSET_YMAX = 0.056
MATRIX_INSET_YTICKS = [0.008, 0.016, 0.024, 0.032, 0.040, 0.048, 0.056]
MATRIX_INSET_XMIN = -0.004
MATRIX_INSET_XMAX = 0.008
MATRIX_FOCUS_BOX = {
    "x": -0.10,
    "y": -1.00,
    "width": 0.32,
    "height": 2.050,
}


def format_runtime_tick(value, _pos):
    abs_value = abs(value)
    if abs_value < 1e-12:
        return "0.00"
    if abs_value >= 100:
        return f"{value:.0f}"
    if abs_value >= 10:
        return f"{value:.1f}"
    if abs_value >= 1:
        return f"{value:.2f}"
    if abs_value >= 0.1:
        return f"{value:.3f}"
    if abs_value >= 0.01:
        return f"{value:.4f}"
    return f"{value:.5f}"


def setup_style():
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def load_series(prefix, sizes, series_dir):
    frames = []
    position_map = {n: i for i, n in enumerate(sizes)}
    for n in sizes:
        csv_path = series_dir / f"{prefix}_n{n}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing CSV file: {csv_path}")
        frame = pd.read_csv(csv_path)
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    data["n"] = data["n"].astype(int)
    data["avg_ms"] = data["avg_ms"].astype(float)
    data["position"] = data["n"].map(position_map)
    return data


def add_matrix_inset(ax, data):
    zoom_ns = [MATRIX_SIZES[0], MATRIX_SIZES[1]]
    zoom_data = data[data["n"].isin(zoom_ns)].copy()
    if zoom_data.empty:
        return

    inset = ax.inset_axes(MATRIX_INSET_BOUNDS)

    for algorithm in MATRIX_ALGORITHMS:
        subset = zoom_data[zoom_data["algorithm"] == algorithm].sort_values("n")
        inset.plot(
            subset["position"],
            subset["avg_ms"],
            color=ALGORITHM_COLORS[algorithm],
            linewidth=2.0,
            zorder=3,
        )
        x0 = float(subset["position"].iloc[0])
        y0 = float(subset["avg_ms"].iloc[0])
        inset.plot(
            [x0],
            [y0],
            color=ALGORITHM_COLORS[algorithm],
            marker=ALGORITHM_MARKERS[algorithm],
            linestyle="None",
            markersize=6.0,
            markerfacecolor="white",
            markeredgewidth=1.2,
            zorder=4,
        )

    inset.set_xlim(MATRIX_INSET_XMIN, MATRIX_INSET_XMAX)
    inset.set_ylim(MATRIX_INSET_YMIN, MATRIX_INSET_YMAX)
    inset.set_xticks([0])
    inset.set_xticklabels([str(zoom_ns[0])], fontsize=8.5)
    inset.tick_params(axis="y", labelsize=8.5)
    inset.yaxis.set_major_formatter(FuncFormatter(format_runtime_tick))
    inset.set_yticks(MATRIX_INSET_YTICKS)
    inset.grid(True, linestyle="--", linewidth=0.6, alpha=0.3)
    for spine in inset.spines.values():
        spine.set_linewidth(1.0)
        spine.set_edgecolor("#666666")

    focus_box = Rectangle(
        (MATRIX_FOCUS_BOX["x"], MATRIX_FOCUS_BOX["y"]),
        MATRIX_FOCUS_BOX["width"],
        MATRIX_FOCUS_BOX["height"],
        fill=False,
        edgecolor="#666666",
        linestyle=(0, (4, 3)),
        linewidth=1.0,
        zorder=3,
    )
    ax.add_patch(focus_box)

    left_top = (
        MATRIX_FOCUS_BOX["x"],
        MATRIX_FOCUS_BOX["y"] + MATRIX_FOCUS_BOX["height"],
    )
    right_top = (
        MATRIX_FOCUS_BOX["x"] + MATRIX_FOCUS_BOX["width"],
        MATRIX_FOCUS_BOX["y"] + MATRIX_FOCUS_BOX["height"],
    )

    left_conn = ConnectionPatch(
        xyA=left_top,
        coordsA=ax.transData,
        xyB=(0.0, 0.0),
        coordsB=inset.transAxes,
        linestyle=(0, (4, 3)),
        linewidth=1.0,
        color="#666666",
        zorder=2,
    )
    right_conn = ConnectionPatch(
        xyA=right_top,
        coordsA=ax.transData,
        xyB=(1.0, 0.0),
        coordsB=inset.transAxes,
        linestyle=(0, (4, 3)),
        linewidth=1.0,
        color="#666666",
        zorder=2,
    )
    ax.add_artist(left_conn)
    ax.add_artist(right_conn)


def plot_curve(data, algorithms, output_path, sizes, tick_labels, x_label, add_inset=False):
    fig, ax = plt.subplots(figsize=(8.7, 5.4))
    positions = list(range(len(sizes)))

    for algorithm in algorithms:
        subset = data[data["algorithm"] == algorithm].sort_values("n")
        ax.plot(
            subset["position"],
            subset["avg_ms"],
            label=ALGORITHM_LABELS[algorithm],
            color=ALGORITHM_COLORS[algorithm],
            marker=ALGORITHM_MARKERS[algorithm],
            linewidth=2.4,
            markersize=7.2,
            markerfacecolor="white",
            markeredgewidth=1.5,
        )

    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel("平均运行时间 (ms)", fontsize=12)
    ax.set_xticks(positions)
    ax.set_xticklabels(tick_labels, fontsize=10.5)
    ax.tick_params(axis="y", labelsize=11)
    ax.yaxis.set_major_formatter(FuncFormatter(format_runtime_tick))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.grid(True, axis="both", linestyle="--", linewidth=0.8, alpha=0.35)
    ax.set_axisbelow(True)
    ax.legend(
        loc="upper left",
        frameon=True,
        framealpha=0.95,
        edgecolor="#cfcfcf",
        fontsize=10.5,
    )

    if add_inset:
        add_matrix_inset(ax, data)

    for spine in ax.spines.values():
        spine.set_linewidth(1.0)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def main():
    setup_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sum_data = load_series("n_number_sum", SUM_SIZES, SUM_SERIES_DIR)
    plot_curve(
        sum_data,
        SUM_ALGORITHMS,
        OUTPUT_DIR / "n_number_sum_runtime_curve.pdf",
        SUM_SIZES,
        SUM_TICK_LABELS,
        "问题规模 n",
    )

    matrix_data = load_series("matrix_vector_dot", MATRIX_SIZES, MATRIX_SERIES_DIR)
    plot_curve(
        matrix_data,
        MATRIX_ALGORITHMS,
        OUTPUT_DIR / "matrix_vector_dot_runtime_curve.pdf",
        MATRIX_SIZES,
        MATRIX_TICK_LABELS,
        "矩阵维度 n（按 cache 阶段选点）",
        add_inset=True,
    )

    print("Saved:", OUTPUT_DIR / "n_number_sum_runtime_curve.pdf")
    print("Saved:", OUTPUT_DIR / "matrix_vector_dot_runtime_curve.pdf")


if __name__ == "__main__":
    main()
