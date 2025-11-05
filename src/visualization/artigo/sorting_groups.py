"""Plotting utilities for sorting_groups outputs.

This module is based on `grouping.py` but adapted to the CSV format used
by `output/sorting_groups/...`: each robot is stored as a group of 6
values per timestamp: x,y,theta, color_r, color_g, color_b (color one-hot).

Usage (CLI):
    python3 src/visualization/artigo/sorting_groups.py --dir \
        "/path/to/output/sorting_groups/31-10-2025 02-14-17"

The script will search generation subfolders (numeric names like `078`),
look for `positions/robots/*.csv` and create a grid of snapshots (rows=
generations, cols=timestamps) where robot trajectories and current
positions are plotted colored by their provided color.
"""
from __future__ import annotations

import os
import glob
from typing import Sequence, Tuple, Optional, List

import numpy as np
import matplotlib.pyplot as plt


def _find_generation_dirs(base_dir: str) -> List[str]:
    dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    # prefer numeric generation directories, sort by numeric value when possible
    numeric = [d for d in dirs if d.isdigit()]
    if numeric:
        numeric.sort(key=lambda x: int(x))
        return [os.path.join(base_dir, d) for d in numeric]
    # fallback: return directories sorted alphabetically
    dirs.sort()
    return [os.path.join(base_dir, d) for d in dirs]


def _find_positions_file_in_gen(gen_dir: str) -> Optional[str]:
    # positions files are under gen_dir/positions/robots/*.csv
    search = os.path.join(gen_dir, "positions", "robots", "*.csv")
    matches = glob.glob(search)
    if not matches:
        # some datasets may have positions at gen_dir/positions/*.csv
        matches = glob.glob(os.path.join(gen_dir, "positions", "*.csv"))
    if not matches:
        return None
    # Only consider files that end with _run0.csv per requirement
    run0_matches = [m for m in matches if m.endswith("_run0.csv")]
    if run0_matches:
        run0_matches.sort()
        return run0_matches[0]
    # if none end with 0.csv, return None (do not fallback to other runs)
    return None


def _read_fitness(gen_dir: str) -> Optional[np.ndarray]:
    path = os.path.join(gen_dir, "fitness.csv")
    if not os.path.exists(path):
        return None
    vals = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                vals.append(float(line))
            except ValueError:
                continue
    return np.array(vals) if vals else None


def _parse_line_with_colors(line: str) -> Tuple[np.ndarray, np.ndarray]:
    """Parse a single CSV line into positions (N,3) and colors (N,3).

    The format is expected as repeating groups of 6 floats: x,y,theta,r,g,b
    where r/g/b are one-hot (1 or 0). If the line length isn't a multiple
    of 6, the trailing incomplete values are trimmed.
    """
    parts = [p for p in line.strip().split(",") if p != ""]
    if not parts:
        return np.empty((0, 3)), np.empty((0, 3))
    vals = np.array([float(p) for p in parts])
    group = 6
    if vals.size < group:
        return np.empty((0, 3)), np.empty((0, 3))
    if vals.size % group != 0:
        vals = vals[: (vals.size // group) * group]
    arr = vals.reshape((-1, group))
    positions = arr[:, :3]
    colors = arr[:, 3:6]
    return positions, colors


def _load_trajectory_up_to(pos_file: str, t: int) -> Tuple[np.ndarray, np.ndarray]:
    """Load trajectory up to timestamp t (inclusive).

    Returns (traj, colors) where traj has shape (M, N, 3) (M time steps,
    N robots) and colors has shape (N, 3). If no data, returns empty arrays.
    Colors are taken from the first non-empty line.
    """
    if not os.path.exists(pos_file):
        return np.empty((0, 3)), np.empty((0, 3))

    lines = []
    colors = None
    # We must count only valid parsed timesteps (non-empty, proper groups)
    # because enumerate() counts raw file lines, which may include blanks or
    # malformed lines and would make t refer to the wrong row. Collect
    # parsed position rows until we have reached the requested timestamp t
    # (inclusive).
    with open(pos_file, "r") as f:
        for line in f:
            if not line.strip():
                continue
            pos, col = _parse_line_with_colors(line)
            if pos.size == 0:
                continue
            if colors is None:
                colors = col
            # ensure consistent robot count across timesteps by trimming to min
            lines.append(pos)
            # stop when we've collected the timestep index t (inclusive)
            if len(lines) - 1 >= t:
                break

    if not lines:
        return np.empty((0, 3)), np.empty((0, 3))

    min_n = min(l.shape[0] for l in lines)
    stacked = np.stack([l[:min_n, :] for l in lines], axis=0)
    if colors is None:
        colors = np.zeros((min_n, 3))
    else:
        if colors.shape[0] > min_n:
            colors = colors[:min_n, :]
    return stacked, colors


def _color_label_from_onehot(onehot: np.ndarray) -> str:
    # expect onehot of length 3
    if onehot[0] == 1:
        return "red"
    if onehot[1] == 1:
        return "green"
    if onehot[2] == 1:
        return "blue"
    return "gray"


def plot_snapshots_grid(
    base_dir: str,
    gens: Optional[Sequence[int]] = None,
    timestamps: Sequence[int] = (0, 100, 200, 400, 1000, 1800),
    out_name: str = "sorting_groups_grid.png",
    arena_xlim: Tuple[float, float] = (0, 450),
    arena_ylim: Tuple[float, float] = (0, 450),
    figsize_per_cell: Tuple[float, float] = (3, 3),
) -> str:
    gen_dirs = _find_generation_dirs(base_dir)
    # By default, only plot the 100th generation directory.
    if gens is None:
        if gen_dirs:
            gen_dirs = [gen_dirs[-1]]
    else:
        # map gens ints to gen dir strings (zero-padded to 3 digits if necessary)
        wanted = [f"{g:03d}" for g in gens]
        gen_dirs = [os.path.join(base_dir, d) for d in os.listdir(base_dir) if d in wanted]

    if not gen_dirs:
        raise FileNotFoundError(f"No generation directories found in {base_dir}")

    grid_rows = len(gen_dirs)
    grid_cols = len(timestamps)

    fig, axes = plt.subplots(
        grid_rows,
        grid_cols,
        figsize=(grid_cols * figsize_per_cell[0], grid_rows * figsize_per_cell[1]),
        squeeze=False,
    )

    for r, gen_dir in enumerate(gen_dirs):
        gen_name = os.path.basename(gen_dir)
        # Prefer the best individual if fitness.csv exists (match its index to a run0 file)
        pos_file = None
        fitness = _read_fitness(gen_dir)
        if fitness is not None and fitness.size > 0:
            best_idx = int(np.argmax(fitness))
            prefix = f"{best_idx:03d}_"
            search1 = os.path.join(gen_dir, "positions", "robots", prefix + "*_run0.csv")
            matches = glob.glob(search1)
            if not matches:
                matches = glob.glob(os.path.join(gen_dir, "positions", prefix + "*_run0.csv"))
            if matches:
                matches.sort()
                pos_file = matches[0]
        # fallback: any run0 positions file
        if pos_file is None:
            pos_file = _find_positions_file_in_gen(gen_dir)
        if pos_file is None:
            for c in range(grid_cols):
                axes[r, c].axis("off")
            continue

        for c, t in enumerate(timestamps):
            ax = axes[r, c]
            traj, colors = _load_trajectory_up_to(pos_file, t)
            if traj.size == 0:
                ax.text(0.5, 0.5, "no data", ha="center", va="center")
                ax.set_xticks([])
                ax.set_yticks([])
                continue

            M, N, _ = traj.shape
            # colors is shape (N, 3) (one-hot) - build labels per robot
            labels = [
                _color_label_from_onehot(colors[i]) if i < colors.shape[0] else "gray"
                for i in range(N)
            ]

            ax.set_aspect("equal")

            # plot trajectories per robot with low alpha
            for i in range(N):
                col = labels[i]
                xs = traj[:, i, 0]
                ys = traj[:, i, 1]
                # draw trajectories under the current-position dots by using a
                # lower zorder for lines and higher for the scatter points
                ax.plot(xs, ys, color=col, alpha=0.2, linewidth=0.9, linestyle='--', zorder=1)

            current = traj[-1]
            xs_cur = current[:, 0]
            ys_cur = current[:, 1]
            colors_plot = [labels[i] for i in range(current.shape[0])]
            # scatter points should appear above the trajectory lines
            ax.scatter(xs_cur, ys_cur, s=30, c=colors_plot, edgecolors='k', linewidths=0.3, zorder=2)

            ax.set_title(f"t={t}")
            ax.set_xlim(*arena_xlim)
            ax.set_ylim(*arena_ylim)
            ax.set_xticks([])
            ax.set_yticks([])

        # annotate row with generation label (left of first column)
        axes[r, 0].text(-0.12, 0.5, f"gen {gen_name}", transform=axes[r, 0].transAxes, rotation=90, va="center")

    plt.tight_layout()
    out_path = os.path.join(base_dir, out_name)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Plot sorting_groups snapshots grid")
    parser.add_argument(
        "--dir",
        dest="base_dir",
        required=False,
        default=os.path.join(os.getcwd(), "output", "sorting_groups", "31-10-2025 02-14-17"),
        help="Path to sorting_groups output folder (contains generation subfolders)",
    )
    default_out = os.path.join(os.path.dirname(__file__), "sorting_groups_grid.png")
    parser.add_argument("--out", dest="out_name", default=default_out, help="Output image file path")
    parser.add_argument("--timestamps", dest="timestamps", nargs="*", type=int,
                        default=[0, 100, 200, 400, 1000, 1800],
                        help="Timestamps (line indices) to render as columns")
    args = parser.parse_args()

    saved = plot_snapshots_grid(args.base_dir, timestamps=tuple(args.timestamps), out_name=args.out_name)
    print(f"Saved grid image to: {saved}")
