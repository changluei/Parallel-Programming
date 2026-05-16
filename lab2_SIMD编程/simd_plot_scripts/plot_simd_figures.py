#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate SIMD experiment figures as PDF files.

This script intentionally uses only the Python standard library.  It writes
small PGFPlots/TikZ sources and compiles them with XeLaTeX, which is already
used by the report.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
LAB_DIR = SCRIPT_DIR.parent
OUT_DIR = LAB_DIR / "SIMD" / "fig"
BUILD_DIR = SCRIPT_DIR / "build"

XELATEX = shutil.which("xelatex") or r"E:\texlive\2025\bin\windows\xelatex.exe"

SIZES = [
    ("fixed5", r"固定$5\times5$"),
    ("rand8", r"随机$8\times8$"),
    ("rank10x8", r"近秩亏$10\times8$"),
    ("rand10x8", r"随机$10\times8$"),
    ("rand1000", r"随机$1000\times1000$"),
]

BASE_DATA = {
    "-O0": {
        "serial": [0.11169, 0.16697, 0.17898, 0.18738, 158294.47],
        "simd": [0.11512, 0.16248, 0.17684, 0.18945, 138616.20],
        "speedup": [0.9702, 1.0276, 1.0121, 0.9891, 1.1420],
    },
    "-O1": {
        "serial": [0.03290, 0.03110, 0.03303, 0.03017, 47072.37],
        "simd": [0.03101, 0.02892, 0.03024, 0.02703, 34199.00],
        "speedup": [1.0612, 1.0754, 1.0922, 1.1162, 1.3764],
    },
    "-O2": {
        "serial": [0.04711, 0.02695, 0.02794, 0.02482, 38588.25],
        "simd": [0.04993, 0.02627, 0.02710, 0.02392, 31265.19],
        "speedup": [0.9437, 1.0260, 1.0311, 1.0378, 1.2342],
    },
}

WIDTH_DATA = {
    "2-way": [0.04993, 0.02627, 0.02710, 0.02392, 31265.19],
    "4-way": [0.04846, 0.02543, 0.02646, 0.02362, 36853.50],
    "8-way": [0.06149, 0.02586, 0.02678, 0.02928, 29376.98],
}

WIDTH_STAGE_1000 = {
    "2-way": {"bidiag": 4244.66, "gkh": 27020.53, "total": 31265.19, "note": ""},
    "4-way": {"bidiag": 4571.87, "gkh": 32281.63, "total": 36853.50, "note": r"，+17.9\%"},
    "8-way": {"bidiag": 3211.25, "gkh": 26165.73, "total": 29376.98, "note": r"，-6.0\%"},
}

BLOCK_STAGE_1000 = {
    "orig": {
        "bidiag": 7973.45,
        "gkh": 30614.80,
        "total": 38588.25,
        "vs_orig": 1.0000,
        "vs_simd": 0.8102,
    },
    "simd": {
        "bidiag": 4244.66,
        "gkh": 27020.53,
        "total": 31265.19,
        "vs_orig": 1.2342,
        "vs_simd": 1.0000,
    },
    "block": {
        "bidiag": 2812.02,
        "gkh": 30286.27,
        "total": 33098.29,
        "vs_orig": 1.1659,
        "vs_simd": 0.9446,
    },
}


def coords(values: list[float]) -> str:
    return " ".join(f"({name},{value:.5g})" for (name, _), value in zip(SIZES, values))


def saving_percent(opt: str) -> list[float]:
    serial = BASE_DATA[opt]["serial"]
    simd = BASE_DATA[opt]["simd"]
    return [(1.0 - s / t) * 100.0 for t, s in zip(serial, simd)]


def relative_to_two_way(kind: str) -> list[float]:
    base = WIDTH_DATA["2-way"]
    return [value / ref for value, ref in zip(WIDTH_DATA[kind], base)]


def tex_header() -> str:
    return r"""
\documentclass[tikz,border=4pt]{standalone}
\usepackage{fontspec}
\usepackage{xeCJK}
\IfFontExistsTF{Arial}{\setmainfont{Arial}}{\setmainfont{TeX Gyre Heros}}
\IfFontExistsTF{Consolas}{\setmonofont{Consolas}}{\setmonofont{Courier New}}
\IfFontExistsTF{Microsoft YaHei}{
  \setCJKmainfont{Microsoft YaHei}
  \setCJKsansfont{Microsoft YaHei}
  \setCJKmonofont{Microsoft YaHei}
}{
  \setCJKmainfont{SimHei}
  \setCJKsansfont{SimHei}
  \setCJKmonofont{SimHei}
}
\usepackage{pgfplots}
\usepgfplotslibrary{groupplots}
\pgfplotsset{compat=1.18}
\definecolor{cBlue}{HTML}{4477AA}
\definecolor{cCyan}{HTML}{66CCEE}
\definecolor{cGreen}{HTML}{228833}
\definecolor{cOrange}{HTML}{CCBB44}
\definecolor{cRed}{HTML}{EE6677}
\definecolor{cPurple}{HTML}{AA3377}
\definecolor{cGray}{HTML}{667085}
\definecolor{cGrid}{HTML}{E0E0E0}
\pgfplotsset{
  nature axis/.style={
    axis x line*=bottom,
    axis y line*=left,
    axis line style={black, line width=1.15pt},
    tick align=outside,
    tick style={black, line width=0.75pt},
    major tick length=3pt,
    minor tick length=2pt,
    clip marker paths=true,
    axis on top=false,
    ymajorgrids=true,
    xmajorgrids=false,
    grid style={draw=cGrid, dashed, line width=0.45pt},
    title style={font=\sffamily\fontsize{12}{14}\selectfont\bfseries},
    label style={font=\sffamily\fontsize{11}{13}\selectfont},
    tick label style={font=\sffamily\fontsize{10}{12}\selectfont},
    legend style={
      font=\sffamily\fontsize{9}{11}\selectfont,
      draw=none,
      fill=none,
      cells={anchor=west},
      /tikz/every even column/.append style={column sep=0.35cm}
    },
  },
  every axis/.append style={
    nature axis
  }
}
"""


def base_figure_tex() -> str:
    size_keys = ",".join(name for name, _ in SIZES)
    tick_labels = ",".join(label for _, label in SIZES)
    return (
        tex_header()
        + rf"""
\begin{{document}}
\begin{{tikzpicture}}
\begin{{axis}}[
  width=13.2cm,
  height=6.0cm,
  ybar,
  bar width=6.0pt,
  ymin=0.90,
  ymax=1.43,
  ylabel={{加速比}},
  symbolic x coords={{{size_keys}}},
  xtick=data,
  xticklabels={{{tick_labels}}},
  x tick label style={{rotate=35, anchor=east}},
  enlarge x limits=0.10,
  legend style={{at={{(0.5,1.07)}}, anchor=south, legend columns=3}},
]
\addplot+[draw=black, line width=0.35pt, fill=cBlue!82] coordinates {{{coords(BASE_DATA["-O0"]["speedup"])}}};
\addplot+[draw=black, line width=0.35pt, fill=cRed!78] coordinates {{{coords(BASE_DATA["-O1"]["speedup"])}}};
\addplot+[draw=black, line width=0.35pt, fill=cGreen!78] coordinates {{{coords(BASE_DATA["-O2"]["speedup"])}}};
\legend{{\texttt{{-O0}}, \texttt{{-O1}}, \texttt{{-O2}}}}
\end{{axis}}
\end{{tikzpicture}}
\end{{document}}
"""
    )


def width_figure_tex() -> str:
    bidiag_coords = " ".join(
        f"({WIDTH_STAGE_1000[key]['bidiag'] / 1000.0:.5f},{key.replace('-', '')})"
        for key in ("2-way", "4-way", "8-way")
    )
    gkh_coords = " ".join(
        f"({WIDTH_STAGE_1000[key]['gkh'] / 1000.0:.5f},{key.replace('-', '')})"
        for key in ("2-way", "4-way", "8-way")
    )
    total_labels = "\n".join(
        rf"\node[anchor=west, font=\sffamily\fontsize{{9}}{{11}}\selectfont, text=cGray] "
        rf"at (axis cs:{WIDTH_STAGE_1000[key]['total'] / 1000.0:.5f},{key.replace('-', '')}) "
        rf"{{{WIDTH_STAGE_1000[key]['total'] / 1000.0:.2f} s{WIDTH_STAGE_1000[key]['note']}}};"
        for key in ("2-way", "4-way", "8-way")
    )
    return (
        tex_header()
        + rf"""
\begin{{document}}
\begin{{tikzpicture}}
\begin{{axis}}[
  width=13.2cm,
  height=5.0cm,
  xbar stacked,
  bar width=13pt,
  xmin=0,
  xmax=50,
  xlabel={{随机 1000×1000 总时间/s}},
  symbolic y coords={{2way,4way,8way}},
  ytick=data,
  yticklabels={{二路 SIMD, 四路展开, 八路展开}},
  enlarge y limits=0.25,
  xmajorgrids=true,
  ymajorgrids=false,
  legend style={{at={{(0.5,1.08)}}, anchor=south, legend columns=2}},
]
\addplot+[draw=black, line width=0.35pt, fill=cBlue!72] coordinates {{{bidiag_coords}}};
\addplot+[draw=black, line width=0.35pt, fill=cRed!58] coordinates {{{gkh_coords}}};
{total_labels}
\legend{{上二对角化, GKH 迭代}}
\end{{axis}}
\end{{tikzpicture}}
\end{{document}}
"""
    )


def block_householder_figure_tex() -> str:
    order = ("orig", "simd", "block")
    bidiag_coords = " ".join(
        f"({BLOCK_STAGE_1000[key]['bidiag'] / 1000.0:.5f},{key})" for key in order
    )
    gkh_coords = " ".join(
        f"({BLOCK_STAGE_1000[key]['gkh'] / 1000.0:.5f},{key})" for key in order
    )
    total_labels = "\n".join(
        rf"\node[anchor=west, font=\sffamily\fontsize{{8.6}}{{10}}\selectfont, text=cGray] "
        rf"at (axis cs:{BLOCK_STAGE_1000[key]['total'] / 1000.0 + 0.55:.5f},{key}) "
        rf"{{{BLOCK_STAGE_1000[key]['total'] / 1000.0:.2f} s}};"
        for key in order
    )
    return (
        tex_header()
        + rf"""
\begin{{document}}
\begin{{tikzpicture}}
\begin{{axis}}[
  width=13.2cm,
  height=5.2cm,
  xbar stacked,
  bar width=13pt,
  xmin=0,
  xmax=45,
  clip=false,
  xlabel={{随机 1000×1000 总时间/s}},
  symbolic y coords={{block,simd,orig}},
  ytick={{orig,simd,block}},
  yticklabels={{原始版本, 二路 SIMD, 分块 Householder + SIMD}},
  enlarge y limits=0.22,
  xmajorgrids=true,
  ymajorgrids=false,
  legend style={{at={{(0.5,1.08)}}, anchor=south, legend columns=2}},
]
\addplot+[draw=black, line width=0.35pt, fill=cBlue!72] coordinates {{{bidiag_coords}}};
\addplot+[draw=black, line width=0.35pt, fill=cRed!58] coordinates {{{gkh_coords}}};
{total_labels}
\legend{{上二对角化, GKH 迭代}}
\end{{axis}}
\end{{tikzpicture}}
\end{{document}}
"""
    )


def compile_tex(tex_name: str, content: str, pdf_name: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    tex_path = BUILD_DIR / tex_name
    tex_path.write_text(content, encoding="utf-8")

    if not Path(XELATEX).exists() and shutil.which(XELATEX) is None:
        raise RuntimeError("xelatex was not found. Please install TeX Live or add xelatex to PATH.")

    cmd = [XELATEX, "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
    for _ in range(2):
        completed = subprocess.run(
            cmd,
            cwd=BUILD_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if completed.returncode != 0:
            log_path = BUILD_DIR / f"{tex_path.stem}.log"
            raise RuntimeError(
                f"XeLaTeX failed for {tex_path.name}.\n"
                f"Log: {log_path}\n\n{completed.stdout[-3000:]}"
            )

    pdf_path = BUILD_DIR / f"{tex_path.stem}.pdf"
    target = OUT_DIR / pdf_name
    shutil.copyfile(pdf_path, target)
    return target


def main() -> None:
    outputs = [
        compile_tex(
            "fig_base_speedup.tex",
            base_figure_tex(),
            "fig_base_speedup.pdf",
        ),
        compile_tex(
            "fig_simd_width_1000_stacked.tex",
            width_figure_tex(),
            "fig_simd_width_1000_stacked.pdf",
        ),
        compile_tex(
            "fig_block_householder_stacked.tex",
            block_householder_figure_tex(),
            "fig_block_householder_stacked.pdf",
        ),
    ]
    print("Generated:")
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
