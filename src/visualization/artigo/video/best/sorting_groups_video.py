"""Produce an MP4 video for the sorting_groups scenario showing best individual's evolution.

Lines use 6-value groups per robot: x,y,theta,r,g,b (one-hot color).
This script maps that to tab:red/green/blue for plotting.
"""
from __future__ import annotations

import os
import glob
import argparse
from typing import Optional, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib import patches


DEFAULT_BASE = os.path.abspath(os.path.join(os.getcwd(), 'output', 'sorting_groups', '31-10-2025 02-14-17'))


def _find_positions_file_in_gen(gen_dir: str) -> Optional[str]:
    search = os.path.join(gen_dir, "positions", "robots", "*.csv")
    matches = glob.glob(search)
    if not matches:
        matches = glob.glob(os.path.join(gen_dir, "positions", "*.csv"))
    if not matches:
        return None
    run0_matches = [m for m in matches if m.endswith("_run0.csv")]
    if run0_matches:
        run0_matches.sort()
        return run0_matches[0]
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
    parts = [p for p in line.strip().split(',') if p != '']
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


def _load_all(pos_file: str) -> Tuple[List[np.ndarray], Optional[np.ndarray]]:
    if not pos_file or not os.path.exists(pos_file):
        return [], None
    lines = []
    colors = None
    with open(pos_file, 'r') as f:
        for raw in f:
            if not raw.strip():
                continue
            pos, col = _parse_line_with_colors(raw)
            if pos.size == 0:
                continue
            if colors is None:
                colors = col
            lines.append(pos)
    return lines, colors


def _onehot_to_color(onehot: np.ndarray) -> str:
    if onehot[0] == 1:
        return 'tab:red'
    if onehot[1] == 1:
        return 'tab:green'
    if onehot[2] == 1:
        return 'tab:blue'
    return 'gray'


def build_video(
    base_dir: str,
    gen: int,
    out_path: str,
    arena_xlim: Tuple[float, float] = (0, 450),
    arena_ylim: Tuple[float, float] = (0, 450),
    width: int = 1280,
    height: int = 720,
    fps: int = 10,
    duration_seconds: int = 180,
):
    gen_dir = os.path.join(base_dir, f"{gen:03d}")
    if not os.path.isdir(gen_dir):
        raise FileNotFoundError(f"Generation directory not found: {gen_dir}")

    fitness = _read_fitness(gen_dir)
    pos_file = None
    if fitness is not None and fitness.size > 0:
        best_idx = int(np.argmax(fitness))
        prefix = f"{best_idx:03d}_"
        matches = glob.glob(os.path.join(gen_dir, 'positions', 'robots', prefix + '*_run0.csv'))
        if not matches:
            matches = glob.glob(os.path.join(gen_dir, 'positions', prefix + '*_run0.csv'))
        if matches:
            matches.sort()
            pos_file = matches[0]

    if pos_file is None:
        pos_file = _find_positions_file_in_gen(gen_dir)

    if pos_file is None:
        raise FileNotFoundError(f"No positions file found in {gen_dir}")

    lines, colors_onehot = _load_all(pos_file)
    total_frames = fps * duration_seconds

    dpi = 100
    figsize = (width / dpi, height / dpi)
    fig = plt.figure(figsize=figsize, dpi=dpi)
    gs = fig.add_gridspec(3, 1, height_ratios=[0.2, 0.6, 0.2])

    fig_top = fig.add_subplot(gs[0, 0])
    arena_ax = fig.add_subplot(gs[1, 0])
    fig_bottom = fig.add_subplot(gs[2, 0])
    fig_top.axis('off')
    fig_bottom.axis('off')

    arena_ax.set_xlim(*arena_xlim)
    arena_ax.set_ylim(*arena_ylim)
    arena_ax.set_aspect('equal')
    arena_ax.set_xticks([])
    arena_ax.set_yticks([])

    arena_rect = patches.Rectangle((arena_xlim[0], arena_ylim[0]), arena_xlim[1]-arena_xlim[0], arena_ylim[1]-arena_ylim[0], fill=False)
    arena_ax.add_patch(arena_rect)

    # prepare stacked trajectories and initial scatter
    stacked = None
    min_n = 0
    if lines:
        min_n = min(l.shape[0] for l in lines)
        stacked = np.stack([l[:min_n, :] for l in lines], axis=0)
        cur = lines[0][:min_n, :]
        xs = cur[:, 0]
        ys = cur[:, 1]
    else:
        xs = np.array([])
        ys = np.array([])

    if colors_onehot is None:
        plot_colors = ['gray' for _ in range(xs.size)]
    else:
        plot_colors = [_onehot_to_color(colors_onehot[i]) if i < colors_onehot.shape[0] else 'gray' for i in range(xs.size)]

    # draw trajectory lines under markers colored per robot
    line_artists = []
    for i in range(min_n):
        col = _onehot_to_color(colors_onehot[i]) if colors_onehot is not None and i < colors_onehot.shape[0] else 'gray'
        ln, = arena_ax.plot([], [], color=col, alpha=0.25, linewidth=0.9, linestyle='--', zorder=1)
        line_artists.append(ln)

    scatter = arena_ax.scatter(xs, ys, s=40, c=plot_colors, edgecolors='k', zorder=5)

    time_text = fig_bottom.text(0.5, 1, 't = 0 seconds', ha='center', va='center', fontsize=16)

    def frame_data(i: int):
        t = i
        if not lines:
            return np.array([]), np.array([]), t
        if t < len(lines):
            arr = lines[t]
        else:
            arr = lines[-1]
        return arr[:, 0], arr[:, 1], t

    def update(i: int):
        xs, ys, t = frame_data(i)
        if xs.size:
            scatter.set_offsets(np.c_[xs, ys])
            if colors_onehot is not None:
                colors_plot = [_onehot_to_color(colors_onehot[j]) if j < colors_onehot.shape[0] else 'gray' for j in range(xs.size)]
                scatter.set_color(colors_plot)
        else:
            scatter.set_offsets(np.empty((0, 2)))

        # update trajectory lines
        if stacked is not None and min_n > 0:
            if t < stacked.shape[0]:
                traj = stacked[: t + 1]
            else:
                traj = stacked
            for j in range(min_n):
                xj = traj[:, j, 0]
                yj = traj[:, j, 1]
                line_artists[j].set_data(xj, yj)

        seconds = i // fps
        time_text.set_text(f"t = {seconds} seconds")
        artists = [scatter, time_text] + line_artists
        return artists

    anim = FuncAnimation(fig, update, frames=total_frames, interval=1000.0/fps, blit=False)
    writer = FFMpegWriter(fps=fps, metadata={'artist': 'auto'}, bitrate=8000)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    anim.save(out_path, writer=writer, dpi=dpi)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description='Render sorting_groups best individual to MP4')
    parser.add_argument('--dir', dest='base_dir', default=DEFAULT_BASE)
    parser.add_argument('--gen', dest='gen', type=int, default=100)
    parser.add_argument('--out', dest='out', default=os.path.join(os.path.dirname(__file__), 'sorting_groups_best.mp4'))
    args = parser.parse_args()
    build_video(args.base_dir, args.gen, args.out)


if __name__ == '__main__':
    main()
