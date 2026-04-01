from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


PROJECT_DIR = Path(__file__).resolve().parents[1]
TEX_PATH = PROJECT_DIR / "main.tex"
OUTPUT_PDF = PROJECT_DIR / "fig" / "matrix_cache_cpi_miss_bar.pdf"

ALGORITHM_LABELS = {
    "平凡算法": "Naive Column Major",
    "优化算法": "Cache Optimized Row Major",
}
ALGORITHM_COLORS = {
    "平凡算法": "#2B7BBC",
    "优化算法": "#D94F45",
}
MISS_COLORS = {
    "L1": "#3B82F6",
    "L2": "#F59E0B",
    "L3": "#10B981",
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


def extract_table_block(tex_text: str) -> str:
    caption = r"\caption{矩阵与向量内积多规模 profiling 结果记录表}"
    caption_index = tex_text.find(caption)
    if caption_index == -1:
        raise RuntimeError("未在 main.tex 中找到矩阵 profiling 表格。")

    table_start = tex_text.rfind(r"\begin{table}[H]", 0, caption_index)
    table_end = tex_text.find(r"\end{table}", caption_index)
    if table_start == -1 or table_end == -1:
        raise RuntimeError("矩阵 profiling 表格环境不完整。")

    return tex_text[table_start:table_end]


def unwrap_multirow(cell: str) -> str:
    cell = cell.strip()
    multirow_match = re.fullmatch(r"\\multirow\{[^}]+\}\{[^}]+\}\{(.+)\}", cell)
    return multirow_match.group(1).strip() if multirow_match else cell


def clean_stage_label(stage: str) -> str:
    text = stage.replace("$", "")
    text = text.replace(r"\mathrm{", "")
    text = text.replace("}", "")
    text = text.replace(r"\approx", "≈")
    text = text.replace(" ", "")
    return text


def parse_pair(pair_text: str) -> tuple[int, int]:
    miss_text, hit_text = pair_text.split("/")
    miss = int(miss_text.replace(",", "").strip())
    hit = int(hit_text.replace(",", "").strip())
    return miss, hit


def to_miss_rate(pair_text: str) -> float:
    miss, hit = parse_pair(pair_text)
    total = miss + hit
    return (miss / total * 100.0) if total else 0.0


def load_matrix_profile_data() -> list[dict]:
    tex_text = TEX_PATH.read_text(encoding="utf-8")
    table_body = extract_table_block(tex_text)

    rows: list[dict] = []
    current_n: int | None = None
    current_stage: str | None = None

    for raw_line in table_body.splitlines():
        line = raw_line.strip()
        if not line.endswith(r"\\"):
            continue
        if "平凡算法" not in line and "优化算法" not in line:
            continue

        cells = [cell.strip() for cell in line[:-2].split("&")]
        if len(cells) != 8:
            raise RuntimeError(f"无法解析矩阵 profiling 行: {line}")

        n_cell, stage_cell, algorithm, cpi_text, l1_pair, l2_pair, l3_pair, cpu_time_text = cells

        if n_cell:
            current_n = int(unwrap_multirow(n_cell))
        if stage_cell:
            current_stage = clean_stage_label(unwrap_multirow(stage_cell))

        if current_n is None or current_stage is None:
            raise RuntimeError(f"矩阵 profiling 表格缺少规模或 cache 阶段信息: {line}")

        rows.append(
            {
                "n": current_n,
                "stage": current_stage,
                "algorithm": algorithm,
                "cpi": float(cpi_text),
                "cpu_time": float(cpu_time_text),
                "l1_rate": to_miss_rate(l1_pair),
                "l2_rate": to_miss_rate(l2_pair),
                "l3_rate": to_miss_rate(l3_pair),
            }
        )

    if not rows:
        raise RuntimeError("矩阵 profiling 表格中没有解析到任何数据行。")
    return rows


def add_point_labels(ax, xs: list[float], ys: list[float], color: str, fmt: str, y_offset: float) -> None:
    for x, y in zip(xs, ys):
        ax.text(
            x,
            y + y_offset,
            fmt.format(y),
            color=color,
            fontsize=8.3,
            ha="center",
            va="bottom",
        )


def style_line_axes(ax, title: str, ylabel: str, positions: list[int], tick_labels: list[str]) -> None:
    ax.set_title(title, fontsize=12, pad=8)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_xticks(positions)
    ax.set_xticklabels(tick_labels, fontsize=10)
    ax.grid(True, linestyle="--", linewidth=0.75, alpha=0.30)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=True, framealpha=0.94, edgecolor="#D0D0D0", fontsize=9.2)


def plot_line_series(ax, grouped: dict[str, list[dict]], pos_map: dict[int, int], y_key: str) -> None:
    marker_map = {"平凡算法": "o", "优化算法": "s"}

    for algorithm in ("平凡算法", "优化算法"):
        subset = grouped[algorithm]
        xs = [pos_map[item["n"]] for item in subset]
        ys = [item[y_key] for item in subset]
        ax.plot(
            xs,
            ys,
            color=ALGORITHM_COLORS[algorithm],
            marker=marker_map[algorithm],
            linewidth=2.3,
            markersize=7,
            markerfacecolor="white",
            markeredgewidth=1.5,
            label=ALGORITHM_LABELS[algorithm],
        )


def plot_grouped_miss_rates(ax, grouped: dict[str, list[dict]], ordered_ns: list[int], tick_labels: list[str]) -> None:
    centers = [index * 1.75 for index in range(len(ordered_ns))]
    cache_offsets = {"L1": -0.34, "L2": 0.0, "L3": 0.34}
    bar_width = 0.11

    for cache_level, offset in cache_offsets.items():
        key = f"{cache_level.lower()}_rate"
        naive_values = [item[key] for item in grouped["平凡算法"]]
        optimized_values = [item[key] for item in grouped["优化算法"]]
        naive_xs = [center + offset - bar_width / 2 for center in centers]
        optimized_xs = [center + offset + bar_width / 2 for center in centers]

        ax.bar(
            naive_xs,
            naive_values,
            width=bar_width,
            color=MISS_COLORS[cache_level],
            edgecolor="#2F2F2F",
            linewidth=0.8,
        )
        ax.bar(
            optimized_xs,
            optimized_values,
            width=bar_width,
            color=MISS_COLORS[cache_level],
            edgecolor="#2F2F2F",
            linewidth=0.8,
            hatch="//",
            alpha=0.72,
        )

        for x in [center + offset for center in centers]:
            ax.text(
                x,
                -0.12,
                cache_level,
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=8.6,
                color=MISS_COLORS[cache_level],
            )

    separator_positions = [(left + right) / 2 for left, right in zip(centers, centers[1:])]
    for separator_x in separator_positions:
        ax.axvline(separator_x, color="#CFCFCF", linestyle="--", linewidth=0.8, zorder=0)

    ax.set_title("Paired Cache Miss Rates by Problem Size", fontsize=12, pad=8)
    ax.set_ylabel("Miss Rate (%)", fontsize=11)
    ax.set_xlabel("Problem Size n", fontsize=11)
    ax.set_xticks(centers)
    ax.set_xticklabels(tick_labels, fontsize=10)
    ax.set_ylim(0, 105)
    ax.set_xlim(centers[0] - 0.72, centers[-1] + 0.72)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.30)
    ax.set_axisbelow(True)

    cache_handles = [
        Patch(facecolor=MISS_COLORS["L1"], edgecolor="#2F2F2F", label="L1 miss rate"),
        Patch(facecolor=MISS_COLORS["L2"], edgecolor="#2F2F2F", label="L2 miss rate"),
        Patch(facecolor=MISS_COLORS["L3"], edgecolor="#2F2F2F", label="L3 miss rate"),
    ]
    algorithm_handles = [
        Patch(facecolor="#9CA3AF", edgecolor="#2F2F2F", label="Naive"),
        Patch(facecolor="#D1D5DB", edgecolor="#2F2F2F", hatch="//", label="Optimized"),
    ]

    cache_legend = ax.legend(
        handles=cache_handles,
        loc="upper left",
        ncol=3,
        frameon=True,
        framealpha=0.94,
        edgecolor="#D0D0D0",
        fontsize=9.2,
    )
    ax.add_artist(cache_legend)
    ax.legend(
        handles=algorithm_handles,
        loc="upper right",
        ncol=2,
        frameon=True,
        framealpha=0.94,
        edgecolor="#D0D0D0",
        fontsize=9.2,
    )


def main() -> None:
    setup_style()
    rows = load_matrix_profile_data()

    ordered_ns = sorted({row["n"] for row in rows})
    stage_by_n = {row["n"]: row["stage"] for row in rows}
    positions = list(range(len(ordered_ns)))
    pos_map = {n: index for index, n in enumerate(ordered_ns)}
    tick_labels = [f"{n}\n{stage_by_n[n]}" for n in ordered_ns]

    grouped = {"平凡算法": [], "优化算法": []}
    for row in rows:
        grouped[row["algorithm"]].append(row)
    for algorithm in grouped:
        grouped[algorithm].sort(key=lambda item: item["n"])

    fig = plt.figure(figsize=(10.8, 8.2))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.18], hspace=0.34, wspace=0.22)
    ax_cpi = fig.add_subplot(grid[0, 0])
    ax_cpu = fig.add_subplot(grid[0, 1])
    ax_miss = fig.add_subplot(grid[1, :])

    plot_line_series(ax_cpi, grouped, pos_map, "cpi")
    plot_line_series(ax_cpu, grouped, pos_map, "cpu_time")
    style_line_axes(ax_cpi, "CPI by Problem Size", "CPI", positions, tick_labels)
    style_line_axes(ax_cpu, "VTune CPU Time by Problem Size", "CPU Time (s)", positions, tick_labels)

    naive_rows = grouped["平凡算法"]
    optimized_rows = grouped["优化算法"]
    add_point_labels(
        ax_cpi,
        [pos_map[item["n"]] for item in naive_rows],
        [item["cpi"] for item in naive_rows],
        ALGORITHM_COLORS["平凡算法"],
        "{:.2f}",
        0.10,
    )
    add_point_labels(
        ax_cpi,
        [pos_map[item["n"]] for item in optimized_rows],
        [item["cpi"] for item in optimized_rows],
        ALGORITHM_COLORS["优化算法"],
        "{:.2f}",
        0.10,
    )
    add_point_labels(
        ax_cpu,
        [pos_map[item["n"]] for item in naive_rows],
        [item["cpu_time"] for item in naive_rows],
        ALGORITHM_COLORS["平凡算法"],
        "{:.3f}",
        0.004,
    )
    add_point_labels(
        ax_cpu,
        [pos_map[item["n"]] for item in optimized_rows],
        [item["cpu_time"] for item in optimized_rows],
        ALGORITHM_COLORS["优化算法"],
        "{:.3f}",
        0.004,
    )

    plot_grouped_miss_rates(ax_miss, grouped, ordered_ns, tick_labels)

    for ax in (ax_cpi, ax_cpu, ax_miss):
        for spine in ax.spines.values():
            spine.set_linewidth(1.0)

    fig.savefig(OUTPUT_PDF, bbox_inches="tight")
    print("Saved matrix profiling figure.")


if __name__ == "__main__":
    main()
