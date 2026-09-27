"""Visualization helpers for grouping outputs.

This module provides a utility to plot snapshots (positions + headings)
of the best individual for selected generations and timestamps.

Usage (module):
	from src.visualization.artigo.grouping import plot_best_snapshots_grid
	plot_best_snapshots_grid('/path/to/output/grouping/20-10-2025 15-47-53')

Usage (CLI):
	python -m src.visualization.artigo.grouping --dir \
	  "/path/to/output/grouping/20-10-2025 15-47-53"

The code assumes each generation folder contains a `fitness.csv` and a
`positions/` directory with per-individual CSVs where each line is a
timestamp and contains comma-separated floats in groups of 3: x,y,theta.
"""
from __future__ import annotations

import os
import glob
from typing import Sequence, Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt


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
				# ignore non-numeric lines
				continue
	return np.array(vals)


def _find_positions_file(gen_dir: str, index: int, replicate_suffix: str = "_1.csv") -> Optional[str]:
	prefix = f"{index:03d}_"
	pattern = os.path.join(gen_dir, "positions", prefix + "*" + replicate_suffix)
	matches = glob.glob(pattern)
	if not matches:
		pattern_any = os.path.join(gen_dir, "positions", prefix + "*.csv")
		matches = glob.glob(pattern_any)
	return matches[0] if matches else None


def _load_positions_at_timestep(pos_file: str, t: int) -> np.ndarray:
	"""Load Nx3 array (x,y,theta) for timestamp t (0-based).

	If t is beyond the file length, returns the last available line.
	If no data, returns an empty array with shape (0,3).
	"""
	if not os.path.exists(pos_file):
		return np.empty((0, 3))
	with open(pos_file, "r") as f:
		for i, line in enumerate(f):
			if i == t:
				line = line.strip()
				if not line:
					return np.empty((0, 3))
				parts = [p for p in line.split(",") if p != ""]
				vals = np.array([float(p) for p in parts])
				if vals.size % 3 != 0:
					vals = vals[: (vals.size // 3) * 3]
				return vals.reshape((-1, 3))
	# fallback: use last non-empty line
	with open(pos_file, "r") as f:
		lines = [l for l in f if l.strip()]
	if not lines:
		return np.empty((0, 3))
	parts = [p for p in lines[-1].strip().split(",") if p != ""]
	vals = np.array([float(p) for p in parts])
	if vals.size % 3 != 0:
		vals = vals[: (vals.size // 3) * 3]
	return vals.reshape((-1, 3))


def _load_trajectory_up_to(pos_file: str, t: int) -> np.ndarray:
	"""Load trajectory up to timestamp t (inclusive).

	Returns array with shape (M, N, 3) where M is number of time-steps read
	(min(t+1, available_lines)) and N is number of robots. If no data,
	returns an empty array with shape (0, 3).
	"""
	if not os.path.exists(pos_file):
		return np.empty((0, 3))

	lines = []
	with open(pos_file, "r") as f:
		for i, line in enumerate(f):
			if not line.strip():
				continue
			parts = [p for p in line.strip().split(",") if p != ""]
			vals = np.array([float(p) for p in parts])
			if vals.size % 3 != 0:
				vals = vals[: (vals.size // 3) * 3]
			arr = vals.reshape((-1, 3))
			lines.append(arr)
			if i >= t:
				break

	if not lines:
		return np.empty((0, 3))

	# Some lines might contain different number of robots; use the minimum
	# so we can stack into a rectangular array.
	min_n = min(l.shape[0] for l in lines)
	stacked = np.stack([l[:min_n, :] for l in lines], axis=0)
	return stacked


def plot_best_snapshots_grid(
	base_dir: str,
	gens: Optional[Sequence[int]] = None,
	timestamps: Sequence[int] = (0, 100, 200, 400, 1000, 1800),
	replicate_suffix: str = "_1.csv",
	out_name: str = "best_snapshots_grid.png",
	arena_xlim: Tuple[float, float] = (0, 316),
	arena_ylim: Tuple[float, float] = (0, 316),
	figsize_per_cell: Tuple[float, float] = (3, 3),
) -> str:
	"""Create and save the grid image, returning the saved path.

	base_dir: generation container folder (contains 000, 001, ...)
	gens: list of generation indices (integers)
	timestamps: list of timestamp line indices to plot
	replicate_suffix: preferred replicate filename suffix
	out_name: output file name saved inside base_dir
	"""
	# If gens is None, pick the last (highest-numbered) generation directory found
	if gens is None:
		gen_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.isdigit()]
		if gen_dirs:
			last = max(int(d) for d in gen_dirs)
			gens = (last,)
		else:
			gens = (0,)

	grid_rows = len(gens)
	grid_cols = len(timestamps)

	fig, axes = plt.subplots(
		grid_rows,
		grid_cols,
		figsize=(grid_cols * figsize_per_cell[0], grid_rows * figsize_per_cell[1]),
		squeeze=False,
	)

	for r, gen in enumerate(gens):
		gen_dir = os.path.join(base_dir, f"{gen:03d}")
		if not os.path.isdir(gen_dir):
			for c in range(grid_cols):
				axes[r, c].axis("off")
			continue

		fitness = _read_fitness(gen_dir)
		if fitness is None or fitness.size == 0:
			for c in range(grid_cols):
				axes[r, c].axis("off")
			continue

		best_idx = int(np.argmax(fitness))
		pos_file = _find_positions_file(gen_dir, best_idx, replicate_suffix)
		if pos_file is None:
			for c in range(grid_cols):
				axes[r, c].axis("off")
			continue

		for c, t in enumerate(timestamps):
			ax = axes[r, c]
			traj = _load_trajectory_up_to(pos_file, t)
			if traj.size == 0:
				ax.text(0.5, 0.5, "no data", ha="center", va="center")
				ax.set_xticks([])
				ax.set_yticks([])
				continue

			# traj shape: (M, N, 3) where M = time steps up to t, N = robots
			ax.set_aspect("equal")

			# plot per-robot continuous trajectories up to timestamp t
			M, N, _ = traj.shape
			for i in range(N):
				xs = traj[:, i, 0]
				ys = traj[:, i, 1]
				ax.plot(xs, ys, color="tab:blue", alpha=0.2, linewidth=1, linestyle='--')

			# overlay current positions (last frame) as points
			current = traj[-1]
			xs_cur = current[:, 0]
			ys_cur = current[:, 1]
			ax.scatter(xs_cur, ys_cur, s=20, c="tab:blue", edgecolors='k', linewidths=0.5, zorder=5)

			ax.set_title(f"t={int(t/10)}s", fontsize=14)
			ax.set_xlim(*arena_xlim)
			ax.set_ylim(*arena_ylim)
			# ✅ Add axis labels and ticks for dimensions
			ax.set_xticks(np.linspace(0, 316, 3))
			ax.set_yticks(np.linspace(0, 316, 3))

	plt.tight_layout()
	out_path = os.path.join(base_dir, out_name)
	fig.savefig(out_path, dpi=200)
	plt.close(fig)
	return out_path


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Plot best individual snapshots grid")
	parser.add_argument("--dir", dest="base_dir", required=False,
						default=os.path.join(os.getcwd(), "output/grouping/20-10-2025 15-47-53"),
						help="Path to grouping output folder (contains generation subfolders)")
	default_out = os.path.join(os.path.dirname(__file__), "aggregation-snapshots.png")
	parser.add_argument("--out", dest="out_name", default=default_out,
						help="Output image file path (absolute or relative). If relative, saved inside --dir; default is the artigo folder")
	args = parser.parse_args()

	saved = plot_best_snapshots_grid(args.base_dir, out_name=args.out_name)
	print(f"Saved grid image to: {saved}")

