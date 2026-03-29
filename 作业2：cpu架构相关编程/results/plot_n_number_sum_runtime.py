from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


RESULTS_DIR = Path(r"E:\桌面\大二下\并行\作业2：cpu架构相关编程\results")
SERIES_DIR = RESULTS_DIR / "series_from_1024_doubling"
OUTPUT_DIR = Path(r"E:\桌面\大二下\并行\作业2：cpu架构相关编程\CPU架构相关编程\fig")
OUTPUT_PDF = OUTPUT_DIR / "n_number_sum_runtime_curve.pdf"

SIZES = [1024, 2048, 4096, 8192, 16384, 32768]
ALGORITHM_ORDER = [
    "naive_chain",
    "two_way_chain",
    "pairwise_reduction",
]
ALGORITHM_LABELS = {
    "naive_chain": "Naive Chain",
    "two_way_chain": "Two-Way Chain",
    "pairwise_reduction": "Pairwise Reduction",
}
ALGORITHM_COLORS = {
    "naive_chain": "#1f77b4",
    "two_way_chain": "#d62728",
    "pairwise_reduction": "#2ca02c",
}
ALGORITHM_MARKERS = {
    "naive_chain": "o",
    "two_way_chain": "s",
    "pairwise_reduction": "^",
}


def load_data() -> pd.DataFrame:
    frames = []
    for n in SIZES:
        csv_path = SERIES_DIR / f"n_number_sum_n{n}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing CSV file: {csv_path}")
        frame = pd.read_csv(csv_path)
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    data["n"] = data["n"].astype(int)
    data["avg_ms"] = data["avg_ms"].astype(float)
    return data


def plot_runtime(data: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "STIX Two Text", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig, ax = plt.subplots(figsize=(8.4, 5.2))

    for algorithm in ALGORITHM_ORDER:
        subset = data[data["algorithm"] == algorithm].sort_values("n")
        ax.plot(
            subset["n"],
            subset["avg_ms"],
            label=ALGORITHM_LABELS[algorithm],
            color=ALGORITHM_COLORS[algorithm],
            marker=ALGORITHM_MARKERS[algorithm],
            linewidth=2.3,
            markersize=7,
            markerfacecolor="white",
            markeredgewidth=1.6,
        )

    ax.set_title("Runtime Comparison for Summing n Numbers", fontsize=15, pad=12)
    ax.set_xlabel(r"Problem Size $n$", fontsize=12)
    ax.set_ylabel("Average Runtime (ms)", fontsize=12)
    ax.set_xticks(SIZES)
    ax.set_xticklabels([rf"$2^{{{n.bit_length() - 1}}}$" for n in SIZES], fontsize=11)
    ax.tick_params(axis="y", labelsize=11)
    ax.grid(True, which="major", linestyle="--", linewidth=0.8, alpha=0.35)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.5, alpha=0.2)
    ax.set_axisbelow(True)
    ax.legend(
        loc="upper right",
        frameon=True,
        framealpha=0.95,
        edgecolor="#cfcfcf",
        fontsize=10.5,
    )
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

    for spine in ax.spines.values():
        spine.set_linewidth(1.0)

    fig.tight_layout()
    fig.savefig(OUTPUT_PDF, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    data = load_data()
    plot_runtime(data)
    print(f"Saved plot to: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
