"""Create a 2x3 grid MP4 video for grouping showing best individuals
from generations [0,20,40,60,80,100].

Each subplot shows the arena evolution for that generation's best individual.
Video is 16:9, 180 seconds long (1800 frames at 10 fps). Top and bottom 20%
are whitespace; the grid occupies the center 60% vertical area. A time counter
is shown below the grid.
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


def find_positions_file_for_index(gen_dir: str, index: int, kind: str = 'robots') -> Optional[str]:
    # The positions files in our output use the layout:
    #   <gen_dir>/positions/<prefix>_<genome>_N.csv
    # (no `robots`/`objects` subdirectories). Match the behavior of the
    # single-best video script: prefer files ending with "_1.csv" and
    # fall back to any CSV that starts with the index prefix.
    dirp = os.path.join(gen_dir, 'positions')
    if not os.path.isdir(dirp):
        return None
    prefix = f"{index:03d}_"
    # prefer the "_1.csv" naming if present
    matches = glob.glob(os.path.join(dirp, prefix + "*" + "_1.csv"))
    if not matches:
        matches = glob.glob(os.path.join(dirp, prefix + "*.csv"))
    return matches[0] if matches else None


def load_all_robot_lines(pos_file: str) -> List[np.ndarray]:
    if not pos_file or not os.path.exists(pos_file):
        return []
    out = []
    with open(pos_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [p for p in line.split(',') if p != '']
            vals = np.array([float(p) for p in parts])
            if vals.size % 3 != 0:
                vals = vals[: (vals.size // 3) * 3]
            if vals.size == 0:
                continue
            out.append(vals.reshape((-1, 3)))
    return out

def build_grid_video(
    base_dir: str,
    gens: List[int],
    out_path: str,
    arena_size: Tuple[float, float] = (316.0, 316.0),
    robot_diam_cm: float = 7.2,
    width: int = 1280,
    height: int = 720,
    fps: int = 10,
    duration_seconds: int = 180,
):
    # load per-generation data
    per_gen = []  # list of dicts with keys: 'lines','objects'
    for gen in gens:
        gen_dir = os.path.join(base_dir, f"{gen:03d}")
        if not os.path.isdir(gen_dir):
            per_gen.append({'lines': [], 'ok': False})
            continue
        fitness = read_fitness(gen_dir)
        if fitness is None or fitness.size == 0:
            per_gen.append({'lines': [], 'ok': False})
            continue
        best_idx = int(np.argmax(fitness))
        robots_file = find_positions_file_for_index(gen_dir, best_idx)
        robot_lines = load_all_robot_lines(robots_file)
        per_gen.append({'lines': robot_lines, 'ok': True})

    total_frames = fps * duration_seconds

    dpi = 100
    figsize = (width / dpi, height / dpi)
    fig = plt.figure(figsize=figsize, dpi=dpi)
    # gridspec: top/bottom whitespace and center 2x3 grid
    gs = fig.add_gridspec(3, 3, height_ratios=[0.2, 0.6, 0.2])

    # top row colspan 3 -> whitespace
    top_ax = fig.add_subplot(gs[0, :])
    top_ax.axis('off')

    # center: create a sub-gridspec (2 rows x 5 cols) inside the middle band
    middle = gs[1, :].subgridspec(2, 5, hspace=0.3, wspace=0.3)
    arena_axes = []
    for r in range(2):
        row_axes = []
        for c in range(5):
            ax = fig.add_subplot(middle[r, c])
            ax.set_xlim(0, arena_size[0])
            ax.set_ylim(0, arena_size[1])
            ax.set_aspect('equal')
            ax.set_xticks([])
            ax.set_yticks([])
            row_axes.append(ax)
        arena_axes.append(row_axes)

    bottom_ax = fig.add_subplot(gs[2, :])
    bottom_ax.axis('off')

    # For each subplot create artists
    artists_per_subplot = []
    for idx, entry in enumerate(per_gen):
        ax = arena_axes[idx // 5][idx % 5]
        if not entry['ok'] or not entry['lines']:
            ax.text(0.5, 0.5, 'no data', ha='center', va='center')
            artists_per_subplot.append({'lines': [], 'scatter': None})
            continue
        # title with generation number
        ax.set_title(f"Generation {gens[idx]}", fontsize=10, pad=4)
        lines = entry['lines']
        min_n = min(l.shape[0] for l in lines)
        stacked = np.stack([l[:min_n, :] for l in lines], axis=0)
        # create per-robot line artists
        line_artists = [ax.plot([], [], color='tab:blue', alpha=0.35, linewidth=0.9, zorder=2)[0] for _ in range(min_n)]
        # initial scatter
        first = lines[0][:min_n, :]
        scatter = ax.scatter(first[:, 0], first[:, 1], s=(robot_diam_cm / 2.0) ** 2, c='tab:blue', edgecolors='k', zorder=5)
        artists_per_subplot.append({'stacked': stacked, 'min_n': min_n, 'lines': line_artists, 'scatter': scatter})

        # # make the black border thinner for better visual subtlety
        # scatter = ax.scatter(
        #     first[:, 0],
        #     first[:, 1],
        #     s=(robot_diam_cm / 2.0) ** 2,
        #     c='tab:blue',
        #     edgecolors='k',
        #     linewidths=0.4,
        #     zorder=5,
        # )
        # artists_per_subplot.append({'stacked': stacked, 'min_n': min_n, 'lines': line_artists, 'scatter': scatter})

    time_text = bottom_ax.text(0.5, 1, 't = 0 seconds', ha='center', va='center', fontsize=16)

    def update(frame_idx: int):
        tstep = frame_idx
        # update each subplot
        for info in artists_per_subplot:
            if 'stacked' not in info:
                continue
            stacked = info['stacked']
            min_n = info['min_n']
            if tstep < stacked.shape[0]:
                traj = stacked[: tstep + 1]
            else:
                traj = stacked
            # update lines
            for j in range(min_n):
                info['lines'][j].set_data(traj[:, j, 0], traj[:, j, 1])
            # update scatter current positions
            last = traj[-1]
            info['scatter'].set_offsets(np.c_[last[:, 0], last[:, 1]])

        seconds = frame_idx // fps
        time_text.set_text(f"t = {seconds} seconds")
        # return lists of artists for blitting (not using blit here)
        return []

    anim = FuncAnimation(fig, update, frames=total_frames, interval=1000.0 / fps, blit=False)
    writer = FFMpegWriter(fps=fps, metadata={'artist': 'auto'}, bitrate=8000)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    anim.save(out_path, writer=writer, dpi=dpi)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description='Render grouping gens grid to MP4')
    parser.add_argument('--dir', dest='base_dir', default=DEFAULT_BASE)
    parser.add_argument('--out', dest='out', default=os.path.join(os.path.dirname(__file__), 'grouping_gens_best.mp4'))
    args = parser.parse_args()
    gens = [0, 2, 5, 10, 20, 30, 40, 60, 80, 100]
    build_grid_video(args.base_dir, gens, args.out)


if __name__ == '__main__':
    main()
