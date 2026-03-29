from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import ConnectionPatch, Rectangle
from matplotlib.ticker import FuncFormatter, MaxNLocator


RESULTS_DIR = Path(r"E:\桌面\大二下\并行\作业2：cpu架构相关编程\results")
SERIES_DIR = RESULTS_DIR / "series_from_1024_doubling"
OUTPUT_DIR = Path(r"E:\桌面\大二下\并行\作业2：cpu架构相关编程\CPU架构相关编程\fig")

SIZES = [1024, 2048, 4096, 8192, 16384]
POSITIONS = list(range(len(SIZES)))
POSITION_MAP = {n: i for i, n in enumerate(SIZES)}

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

# You can tune these two blocks directly.
MATRIX_INSET_BOUNDS = [0.09, 0.22, 0.28, 0.28]
MATRIX_FOCUS_BOX = {
    "x": -0.10,
    "y": -100.0,
    "width": 1.20,
    "height": 250.0,
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
    if abs_value >= 0.001:
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


def load_series(prefix: str) -> pd.DataFrame:
    frames = []
    for n in SIZES:
        csv_path = SERIES_DIR / f"{prefix}_n{n}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing CSV file: {csv_path}")
        frame = pd.read_csv(csv_path)
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    data["n"] = data["n"].astype(int)
    data["avg_ms"] = data["avg_ms"].astype(float)
    data["position"] = data["n"].map(POSITION_MAP)
    return data


def add_matrix_inset(ax, data: pd.DataFrame) -> None:
    zoom_data = data[data["n"].isin([1024, 2048])].copy()
    if zoom_data.empty:
        return

    inset = ax.inset_axes(MATRIX_INSET_BOUNDS)

    for algorithm in MATRIX_ALGORITHMS:
        subset = zoom_data[zoom_data["algorithm"] == algorithm].sort_values("n")
        inset.plot(
            subset["position"],
            subset["avg_ms"],
            color=ALGORITHM_COLORS[algorithm],
            marker=ALGORITHM_MARKERS[algorithm],
            linewidth=2.0,
            markersize=5.4,
            markerfacecolor="white",
            markeredgewidth=1.2,
        )

    inset.set_xlim(-0.12, 1.12)
    inset.set_ylim(0.0, 22.0)
    inset.set_xticks([0, 1])
    inset.set_xticklabels([r"$2^{10}$", r"$2^{11}$"], fontsize=8.5)
    inset.tick_params(axis="y", labelsize=8.5)
    inset.yaxis.set_major_formatter(FuncFormatter(format_runtime_tick))
    inset.yaxis.set_major_locator(MaxNLocator(nbins=5))
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

    left_top = (MATRIX_FOCUS_BOX["x"], MATRIX_FOCUS_BOX["y"] + MATRIX_FOCUS_BOX["height"])
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


def plot_curve(data: pd.DataFrame, algorithms: list[str], title: str, output_path: Path, add_inset: bool = False) -> None:
    fig, ax = plt.subplots(figsize=(8.6, 5.3))

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
    ax.set_xlabel("程序循环次数", fontsize=12)
    ax.set_ylabel("平均运行时间 (ms)", fontsize=12)
    ax.set_xticks(POSITIONS)
    ax.set_xticklabels([rf"$2^{{{n.bit_length() - 1}}}$" for n in SIZES], fontsize=11)
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

    sum_data = load_series("n_number_sum")
    plot_curve(
        sum_data,
        SUM_ALGORITHMS,
        "n 个数求和性能折线图",
        OUTPUT_DIR / "n_number_sum_runtime_curve.pdf",
    )

    matrix_data = load_series("matrix_vector_dot")
    plot_curve(
        matrix_data,
        MATRIX_ALGORITHMS,
        "矩阵与向量内积性能折线图",
        OUTPUT_DIR / "matrix_vector_dot_runtime_curve.pdf",
        add_inset=True,
    )

    print("Saved:", OUTPUT_DIR / "n_number_sum_runtime_curve.pdf")
    print("Saved:", OUTPUT_DIR / "matrix_vector_dot_runtime_curve.pdf")


if __name__ == "__main__":
    main()
