"""Produce an MP4 video for the grouping scenario showing best individual's evolution.

Uses the same conventions as `src.visualization.artigo.grouping` for file layout.
Reserves 20% whitespace top and bottom and shows a time counter under the arena.
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


DEFAULT_BASE = os.path.abspath(os.path.join(os.getcwd(), 'output', 'grouping', '20-10-2025 15-47-53'))


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
    return np.array(vals)


def _find_positions_file(gen_dir: str, index: int) -> Optional[str]:
    prefix = f"{index:03d}_"
    pattern = os.path.join(gen_dir, "positions", prefix + "*" + "_1.csv")
    matches = glob.glob(pattern)
    if not matches:
        matches = glob.glob(os.path.join(gen_dir, "positions", prefix + "*.csv"))
    return matches[0] if matches else None


def _load_all_lines(pos_file: str) -> List[np.ndarray]:
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


def build_video(
    base_dir: str,
    gen: int,
    out_path: str,
    arena_xlim: Tuple[float, float] = (0, 316),
    arena_ylim: Tuple[float, float] = (0, 316),
    width: int = 1280,
    height: int = 720,
    fps: int = 10,
    duration_seconds: int = 180,
):
    gen_dir = os.path.join(base_dir, f"{gen:03d}")
    if not os.path.isdir(gen_dir):
        raise FileNotFoundError(f"Generation directory not found: {gen_dir}")

    fitness = _read_fitness(gen_dir)
    if fitness is None or fitness.size == 0:
        raise FileNotFoundError(f"No fitness.csv or empty under {gen_dir}")
    best_idx = int(np.argmax(fitness))

    pos_file = _find_positions_file(gen_dir, best_idx)
    if pos_file is None:
        raise FileNotFoundError(f"No positions file for best index {best_idx} in {gen_dir}")

    lines = _load_all_lines(pos_file)

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

    # draw trajectory lines under markers
    line_artists = []
    for i in range(min_n):
        ln, = arena_ax.plot([], [], color='tab:blue', alpha=0.25, linewidth=1.0, linestyle='--', zorder=2)
        line_artists.append(ln)

    scatter = arena_ax.scatter(xs, ys, s=40, c='tab:blue', edgecolors='k', zorder=5)

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
    parser = argparse.ArgumentParser(description='Render grouping best individual to MP4')
    parser.add_argument('--dir', dest='base_dir', default=DEFAULT_BASE)
    parser.add_argument('--gen', dest='gen', type=int, default=100)
    parser.add_argument('--out', dest='out', default=os.path.join(os.path.dirname(__file__), 'grouping_best.mp4'))
    args = parser.parse_args()
    build_video(args.base_dir, args.gen, args.out)


if __name__ == '__main__':
    main()
