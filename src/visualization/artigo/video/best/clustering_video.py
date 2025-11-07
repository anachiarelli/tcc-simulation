"""Create an MP4 video for the object_clustering scenario showing the
best individual's run evolution.

Video characteristics:
- MP4 format, 16:9 resolution (default 1280x720)
- Exactly 180 seconds long at 10 timesteps per second (1800 frames)
- Single arena in center with 20% white space top and bottom
- Time counter displayed under the arena: "t = XX seconds"

This script re-uses the input/layout conventions from
`src/visualization/artigo/clustering.py` for file discovery and parsing.
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


DEFAULT_BASE = os.path.abspath(os.path.join(os.getcwd(), 'output', 'object_clustering', '06-11-2025 01-59-33'))


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
    dirp = os.path.join(gen_dir, 'positions', kind)
    if not os.path.isdir(dirp):
        return None
    prefix = f"{index:03d}_"
    matches = glob.glob(os.path.join(dirp, prefix + "*" + "_run2.csv"))
    if not matches:
        matches = glob.glob(os.path.join(dirp, prefix + "*.csv"))
    return matches[0] if matches else None


def load_all_robot_lines(pos_file: str) -> List[np.ndarray]:
    """Return list of arrays shape (N,3) per timestep.
    If file missing, returns empty list.
    """
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


def load_all_object_lines(pos_file: str) -> List[np.ndarray]:
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
            if vals.size % 2 != 0:
                vals = vals[: (vals.size // 2) * 2]
            if vals.size == 0:
                continue
            out.append(vals.reshape((-1, 2)))
    return out


def build_video(
    base_dir: str,
    gen: int,
    out_path: str,
    arena_size: Tuple[float, float] = (112.0, 112.0),
    robot_diam_cm: float = 7.2,
    object_diam_cm: float = 10.0,
    width: int = 1280,
    height: int = 720,
    fps: int = 10,
    duration_seconds: int = 180,
):
    gen_dir = os.path.join(base_dir, f"{gen:03d}")
    if not os.path.isdir(gen_dir):
        raise FileNotFoundError(f"Generation directory not found: {gen_dir}")

    fitness = read_fitness(gen_dir)
    if fitness is None or fitness.size == 0:
        raise FileNotFoundError(f"No fitness.csv or empty under {gen_dir}")
    best_idx = int(np.argmax(fitness))

    robots_file = find_positions_file_for_index(gen_dir, best_idx, kind='robots')
    objects_file = find_positions_file_for_index(gen_dir, best_idx, kind='objects')

    robot_lines = load_all_robot_lines(robots_file)
    object_lines = load_all_object_lines(objects_file) if objects_file else []

    total_frames = fps * duration_seconds

    # Prepare figure with top/bottom white space: use GridSpec ratios 0.2/0.6/0.2
    dpi = 100
    figsize = (width / dpi, height / dpi)
    fig = plt.figure(figsize=figsize, dpi=dpi)
    gs = fig.add_gridspec(3, 1, height_ratios=[0.2, 0.6, 0.2])

    top_ax = fig.add_subplot(gs[0, 0])
    arena_ax = fig.add_subplot(gs[1, 0])
    bottom_ax = fig.add_subplot(gs[2, 0])

    # clean top/bottom axes
    top_ax.axis('off')
    bottom_ax.axis('off')

    # Arena axis setup
    arena_ax.set_xlim(0, arena_size[0])
    arena_ax.set_ylim(0, arena_size[1])
    arena_ax.set_aspect('equal')
    arena_ax.set_xticks([])
    arena_ax.set_yticks([])

    # Draw arena border
    arena_rect = patches.Rectangle((0, 0), arena_size[0], arena_size[1], fill=False, linewidth=1.0)
    arena_ax.add_patch(arena_rect)

    # Prepare per-robot trajectories (stack timesteps) and initial scatter
    stacked = None
    min_n = 0
    if robot_lines:
        min_n = min(l.shape[0] for l in robot_lines)
        stacked = np.stack([l[:min_n, :] for l in robot_lines], axis=0)  # shape (M, N, 3)
        first = robot_lines[0][:min_n, :]
        xs = first[:, 0]
        ys = first[:, 1]
    else:
        xs = np.array([])
        ys = np.array([])

    # trajectory lines under the robot markers
    line_artists = []
    for i in range(min_n):
        ln, = arena_ax.plot([], [], color='tab:blue', alpha=0.35, linewidth=0.9, zorder=2)
        line_artists.append(ln)

    robot_scatter = arena_ax.scatter(xs, ys, s=(robot_diam_cm * 2.0) ** 2, c='tab:blue', edgecolors='k', zorder=5)

    # object patches
    obj_patches: List[patches.Circle] = []
    if object_lines:
        objs0 = object_lines[0]
        for (x, y) in objs0:
            c = patches.Circle((x, y), radius=object_diam_cm / 2.0, facecolor='tab:red', edgecolor='k', linewidth=0.3, zorder=4)
            arena_ax.add_patch(c)
            obj_patches.append(c)

    # time counter text in bottom area (centered)
    time_text = bottom_ax.text(0.5, 1, 't = 0 seconds', ha='center', va='center', fontsize=16)

    def frame_data(idx: int):
        # idx is frame index 0..total_frames-1, map to timestep index (one line per timestep)
        timestep = idx
        # if robot_lines shorter, use last
        if not robot_lines:
            return np.array([]), np.array([]), []
        if timestep < len(robot_lines):
            arr = robot_lines[timestep]
        else:
            arr = robot_lines[-1]
        return arr[:, 0], arr[:, 1], timestep

    def update(frame_idx: int):
        xs, ys, tstep = frame_data(frame_idx)
        # update scatter
        if xs.size:
            robot_scatter.set_offsets(np.c_[xs, ys])
        else:
            robot_scatter.set_offsets(np.empty((0, 2)))

        # update objects
        if object_lines and obj_patches:
            if tstep < len(object_lines):
                objs = object_lines[tstep]
            else:
                objs = object_lines[-1]
            # if number of objects changed, adjust patches count
            for i, p in enumerate(obj_patches):
                if i < objs.shape[0]:
                    p.center = (objs[i, 0], objs[i, 1])

        # update trajectories (show full history up to current timestep)
        if stacked is not None and min_n > 0:
            if tstep < stacked.shape[0]:
                traj = stacked[: tstep + 1]
            else:
                traj = stacked
            # traj shape: (M, N, 3)
            for i in range(min_n):
                xi = traj[:, i, 0]
                yi = traj[:, i, 1]
                line_artists[i].set_data(xi, yi)

        # update time display (seconds)
        seconds = frame_idx // fps
        time_text.set_text(f"t = {seconds} seconds")

        artists = [robot_scatter, time_text] + line_artists
        return artists

    anim = FuncAnimation(fig, update, frames=total_frames, interval=1000.0 / fps, blit=False)

    # Save with FFMpegWriter
    writer = FFMpegWriter(fps=fps, metadata={'artist': 'auto'}, bitrate=8000)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    anim.save(out_path, writer=writer, dpi=dpi)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description='Render clustering best individual to MP4')
    parser.add_argument('--dir', dest='base_dir', default=DEFAULT_BASE, help='Base run folder containing generation subfolders')
    parser.add_argument('--gen', dest='gen', type=int, default=100, help='Generation index to read')
    parser.add_argument('--out', dest='out', default=os.path.join(os.path.dirname(__file__), 'clustering_best.mp4'), help='Output MP4 path')
    args = parser.parse_args()
    build_video(args.base_dir, args.gen, args.out)


if __name__ == '__main__':
    main()
