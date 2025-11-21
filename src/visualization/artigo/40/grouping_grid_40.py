"""Render a 5x8 grid (40 subplots) showing all individuals of a generation for the 'grouping' scenario.

This mirrors the behavior of `grouping_video.py` but displays 40 individuals in a 5x8 grid,
sorted by fitness (highest first), with a single time counter under the grid.
"""
from __future__ import annotations

import os
import glob
import argparse
from typing import Optional, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.animation import FuncAnimation, FFMpegWriter


import os
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed


DEFAULT_BASE = os.path.abspath(os.path.join(os.getcwd(), 'output', 'grouping', '20-10-2025 15-47-53'))


def read_fitness(gen_dir: str) -> Optional[np.ndarray]:
    path = os.path.join(gen_dir, 'fitness.csv')
    if not os.path.exists(path):
        return None
    vals = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                vals.append(float(line))
            except ValueError:
                continue
    return np.array(vals)


def find_positions_file_for_index(gen_dir: str, index: int) -> Optional[str]:
    prefix = f"{index:03d}_"
    pattern = os.path.join(gen_dir, "positions", prefix + "*" + "_1.csv")
    matches = glob.glob(pattern)
    if not matches:
        matches = glob.glob(os.path.join(gen_dir, "positions", prefix + "*.csv"))
    return matches[0] if matches else None


def load_all_robot_lines(pos_file: str) -> List[np.ndarray]:
    if not pos_file or not os.path.exists(pos_file):
        return []
    lines = []
    with open(pos_file, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            parts = [p for p in line.strip().split(',') if p != '']
            vals = np.array([float(p) for p in parts])
            if vals.size % 3 != 0:
                vals = vals[: (vals.size // 3) * 3]
            if vals.size == 0:
                continue
            lines.append(vals.reshape((-1, 3)))
    return lines


def build_video_grid(
    base_dir: str,
    gen: int,
    out_path: str,
    arena_xlim: Tuple[float, float] = (0, 316),
    arena_ylim: Tuple[float, float] = (0, 316),
    robot_diam: float = 7.2,
    width: int = 1280,
    height: int = 720,
    fps: int = 10,
    duration_seconds: int = 180,
    rows: int = 4,
    cols: int = 10,
):
    gen_dir = os.path.join(base_dir, f"{gen:03d}")
    if not os.path.isdir(gen_dir):
        raise FileNotFoundError(f"Generation directory not found: {gen_dir}")

    total_frames = fps * duration_seconds
    n_plots = rows * cols

    # load data for all indices 0..n_plots-1
    individuals = []
    for idx in range(n_plots):
        robots_file = find_positions_file_for_index(gen_dir, idx)
        robot_lines = load_all_robot_lines(robots_file)
        individuals.append({'idx': idx, 'robot_lines': robot_lines, 'robots_file': robots_file})

    fitness = read_fitness(gen_dir)

    dpi = 100
    figsize = (width / dpi, height / dpi)
    fig = plt.figure(figsize=figsize, dpi=dpi)
    gs = fig.add_gridspec(2, 1, height_ratios=[0.94, 0.06])
    grid_gs = gs[0].subgridspec(rows, cols)

    # ordering by fitness
    if fitness is not None and fitness.size > 0:
        fitness_for_idxs = np.full(n_plots, -np.inf)
        ncopy = min(fitness.size, n_plots)
        fitness_for_idxs[:ncopy] = fitness[:ncopy]
        order = list(np.argsort(fitness_for_idxs)[::-1])
    else:
        order = list(range(n_plots))
    ordered = [individuals[j] for j in order]

    for pos, ind in enumerate(ordered):
        r = pos // cols
        c = pos % cols
        ax = fig.add_subplot(grid_gs[r, c])
        ax.set_xlim(*arena_xlim)
        ax.set_ylim(*arena_ylim)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
        arena_rect = patches.Rectangle((arena_xlim[0], arena_ylim[0]), arena_xlim[1]-arena_xlim[0], arena_ylim[1]-arena_ylim[0], fill=False, linewidth=0.6)
        ax.add_patch(arena_rect)

        robot_lines = ind['robot_lines']
        if robot_lines:
            num_robots = min(l.shape[0] for l in robot_lines)
            stacked = np.stack([l[:num_robots, :] for l in robot_lines], axis=0)
            ind['stacked'] = stacked
            ind['num_robots'] = num_robots
            first = robot_lines[0][:num_robots, :]
            xs = first[:, 0]
            ys = first[:, 1]
        else:
            ind['stacked'] = None
            ind['num_robots'] = 0
            xs = np.array([])
            ys = np.array([])

        robot_patches: List[patches.Circle] = []
        for (x, y) in zip(xs, ys):
            # ROBOT DIAMETER NOT DIVIDED BY 2
            rp = patches.Circle((x, y), radius=robot_diam, facecolor='tab:blue', edgecolor='k', linewidth=0.3, zorder=5)
            ax.add_patch(rp)
            robot_patches.append(rp)
        ind['robot_patches'] = robot_patches

        line_artists = []
        for j in range(ind['num_robots']):
            ln, = ax.plot([], [], color='tab:blue', alpha=0.10, linewidth=0.9, zorder=2)
            line_artists.append(ln)
        ind['line_artists'] = line_artists

        ind['ax'] = ax
        # show fitness if available
        orig_idx = ind.get('idx')
        if fitness is not None and orig_idx is not None and orig_idx < fitness.size:
            ax.set_title(f"f = {fitness[orig_idx]:.3f}", fontsize=7, pad=1)

    plt.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.04, wspace=0.06, hspace=0.06)

    bottom_ax = fig.add_subplot(gs[1, 0])
    bottom_ax.axis('off')
    time_text = bottom_ax.text(0.94, 0.5, 't = 0s', ha='center', va='center', fontsize=14)

    def frame_data(idx_frame: int):
        return idx_frame

    def update(frame_idx: int):
        t = frame_idx
        artists = []
        for ind in ordered:
            robot_lines = ind['robot_lines']
            if robot_lines:
                if t < len(robot_lines):
                    arr = robot_lines[t]
                else:
                    arr = robot_lines[-1]
                num = min(arr.shape[0], ind.get('num_robots', 0))
                for j in range(ind.get('num_robots', 0)):
                    if j < num:
                        ind['robot_patches'][j].center = (arr[j, 0], arr[j, 1])
                    else:
                        ind['robot_patches'][j].center = (-1000, -1000)

                stacked = ind.get('stacked', None)
                if stacked is not None and ind['num_robots'] > 0:
                    if t < stacked.shape[0]:
                        traj = stacked[: t + 1]
                    else:
                        traj = stacked
                    for j in range(ind['num_robots']):
                        xi = traj[:, j, 0]
                        yi = traj[:, j, 1]
                        ind['line_artists'][j].set_data(xi, yi)
                        artists.append(ind['line_artists'][j])

            for rp in ind.get('robot_patches', []):
                artists.append(rp)

        seconds = frame_idx // fps
        time_text.set_text(f"t = {seconds}s")
        artists.append(time_text)
        return artists

    anim = FuncAnimation(fig, update, frames=total_frames, interval=1000.0/fps, blit=False)
    writer = FFMpegWriter(fps=fps, metadata={'artist': 'auto'}, bitrate=8000)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    anim.save(out_path, writer=writer, dpi=dpi)
    plt.close(fig)


def render_generation(generation):
    parser = argparse.ArgumentParser(description='Render 5x8 grid of clustering individuals to MP4')
    parser.add_argument('--dir', dest='base_dir', default=DEFAULT_BASE, help='Base run folder containing generation subfolders')
    parser.add_argument('--gen', dest='gen', type=int, default=generation, help='Generation index to read')
    filename = os.path.join(os.path.dirname(__file__), f'grouping_{generation}.mp4')
    parser.add_argument('--out', dest='out', default=filename, help='Output MP4 path')
    args = parser.parse_args([])  # Pass empty list to avoid reading sys.argv
    build_video_grid(args.base_dir, args.gen, args.out)
    return generation

if __name__ == "__main__":
    gens = [0, 15, 75, 90, 100]

    with ProcessPoolExecutor(max_workers=5) as executor:  # adjust workers as needed
        futures = {executor.submit(render_generation, gen): gen for gen in gens}
        for future in as_completed(futures):
            gen = futures[future]
            try:
                future.result()
                print(f"✅ Finished rendering generation {gen}")
            except Exception as e:
                print(f"❌ Error rendering generation {gen}: {e}")
