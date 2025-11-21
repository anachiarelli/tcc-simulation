"""Render a 5x8 grid (40 subplots) showing all individuals of a generation.

Assumptions:
- The generation folder contains position files organized the same way as
  `src/visualization/artigo/video/best/clustering_video.py` expects:
  positions/robots and positions/objects with files named like
  ``{idx:03d}_*.csv`` where each line is a timestep.
- The generation has up to 40 individuals; this script will attempt indices
  0..39 and place each one in a subplot (5 rows x 8 cols). If a file is
  missing the corresponding subplot will remain empty.

Usage: run as a script. It writes an MP4 showing all individuals simultaneously
with a single time counter under the grid.
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


DEFAULT_BASE = os.path.abspath(os.path.join(os.getcwd(), 'output', 'object_clustering', '06-11-2025 01-59-33'))


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


def build_video_grid(
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
    rows: int = 4,
    cols: int = 10,
):
    gen_dir = os.path.join(base_dir, f"{gen:03d}")
    if not os.path.isdir(gen_dir):
        raise FileNotFoundError(f"Generation directory not found: {gen_dir}")

    total_frames = fps * duration_seconds
    n_plots = rows * cols

    # Load per-individual data
    individuals = []
    max_timesteps = 0
    for idx in range(n_plots):
        robots_file = find_positions_file_for_index(gen_dir, idx, kind='robots')
        objects_file = find_positions_file_for_index(gen_dir, idx, kind='objects')
        robot_lines = load_all_robot_lines(robots_file)
        object_lines = load_all_object_lines(objects_file) if objects_file else []
        if robot_lines:
            max_timesteps = max(max_timesteps, len(robot_lines))
        if object_lines:
            max_timesteps = max(max_timesteps, len(object_lines))
        individuals.append({
            'idx': idx,
            'robot_lines': robot_lines,
            'object_lines': object_lines,
            'robots_file': robots_file,
            'objects_file': objects_file,
        })

    # read fitness (optional) so we can label each subplot
    fitness = read_fitness(gen_dir)

    # Prepare figure: grid + bottom time area
    dpi = 100
    figsize = (width / dpi, height / dpi)
    fig = plt.figure(figsize=figsize, dpi=dpi)
    # main grid and a small bottom area for time
    gs = fig.add_gridspec(2, 1, height_ratios=[0.94, 0.06])
    grid_gs = gs[0].subgridspec(rows, cols)

    # create axes ordered by fitness (descending) if fitness is available
    if fitness is not None and fitness.size > 0:
        fitness_for_idxs = np.full(n_plots, -np.inf)
        ncopy = min(fitness.size, n_plots)
        fitness_for_idxs[:ncopy] = fitness[:ncopy]
        order = list(np.argsort(fitness_for_idxs)[::-1])
    else:
        order = list(range(n_plots))

    ordered_individuals = [individuals[j] for j in order]

    for pos, ind in enumerate(ordered_individuals):
        r = pos // cols
        c = pos % cols
        ax = fig.add_subplot(grid_gs[r, c])
        ax.set_xlim(0, arena_size[0])
        ax.set_ylim(0, arena_size[1])
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
        # draw border
        arena_rect = patches.Rectangle((0, 0), arena_size[0], arena_size[1], fill=False, linewidth=0.6)
        ax.add_patch(arena_rect)

        # prepare scatter and trajectory lines
        robot_lines = ind['robot_lines']
        if robot_lines:
            num_robots = min(l.shape[0] for l in robot_lines)
            # stack timesteps -> shape (T, M, 3)
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

        # robot patches (use Circle in data units so size matches arena)
        robot_patches: List[patches.Circle] = []
        for (x, y) in zip(xs, ys):
            rp = patches.Circle((x, y), radius=robot_diam_cm / 2.0, facecolor='tab:blue', edgecolor='k', linewidth=0.3, zorder=5)
            ax.add_patch(rp)
            robot_patches.append(rp)
        ind['robot_patches'] = robot_patches

        # trajectory lines
        line_artists = []
        for j in range(ind['num_robots']):
            ln, = ax.plot([], [], color='tab:blue', alpha=0.35, linewidth=0.7, zorder=2)
            line_artists.append(ln)
        ind['line_artists'] = line_artists

        # objects
        obj_patches: List[patches.Circle] = []
        if ind['object_lines']:
            objs0 = ind['object_lines'][0]
            for (x, y) in objs0:
                c = patches.Circle((x, y), radius=object_diam_cm / 2.0, facecolor='tab:red', edgecolor='k', linewidth=0.3, zorder=4)
                ax.add_patch(c)
                obj_patches.append(c)
        ind['obj_patches'] = obj_patches
        ind['ax'] = ax
        # show fitness above plot if available (use individual's original index)
        orig_idx = ind.get('idx', None)
        if fitness is not None and orig_idx is not None and orig_idx < fitness.size:
            # small font so it fits in tight grid
            ax.set_title(f"f = {fitness[orig_idx]:.3f}", fontsize=7, pad=1)
    # tighten spacing between subplots and reduce margins so the grid is denser
    # left/right/top/bottom chosen to leave small space for border and time area
    # leave more whitespace at the top and less at the bottom
    plt.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.04, wspace=0.06, hspace=0.06)

    # bottom axis for time only
    bottom_ax = fig.add_subplot(gs[1, 0])
    bottom_ax.axis('off')
    time_text = bottom_ax.text(0.94, 0.5, 't = 0s', ha='center', va='center', fontsize=14)

    def frame_data(idx_frame: int):
        # map frames to timestep index (clip to last available)
        tstep = idx_frame
        return tstep

    def update(frame_idx: int):
        tstep = frame_data(frame_idx)
        artists = []
        for ind in individuals:
            ax = ind['ax']
            robot_lines = ind['robot_lines']
            object_lines = ind['object_lines']

            # update robots (patch centers)
            if robot_lines:
                if tstep < len(robot_lines):
                    arr = robot_lines[tstep]
                else:
                    arr = robot_lines[-1]
                num = min(arr.shape[0], ind.get('num_robots', 0))
                for j in range(ind.get('num_robots', 0)):
                    if j < num:
                        ind['robot_patches'][j].center = (arr[j, 0], arr[j, 1])
                    else:
                        # move off-screen if missing
                        ind['robot_patches'][j].center = (-1000, -1000)

                # update trajectories
                stacked = ind.get('stacked', None)
                if stacked is not None and ind['num_robots'] > 0:
                    if tstep < stacked.shape[0]:
                        traj = stacked[: tstep + 1]
                    else:
                        traj = stacked
                    for j in range(ind['num_robots']):
                        xi = traj[:, j, 0]
                        yi = traj[:, j, 1]
                        ind['line_artists'][j].set_data(xi, yi)
                        artists.append(ind['line_artists'][j])

            # update objects
            if object_lines and ind['obj_patches'] is not None:
                if tstep < len(object_lines):
                    objs = object_lines[tstep]
                else:
                    objs = object_lines[-1]
                # ensure patches match count (create extra if needed)
                if objs.shape[0] > len(ind['obj_patches']):
                    # create extra patches
                    for k in range(len(ind['obj_patches']), objs.shape[0]):
                        c = patches.Circle((0, 0), radius=object_diam_cm / 2.0, facecolor='tab:red', edgecolor='k', linewidth=0.3, zorder=4)
                        ind['ax'].add_patch(c)
                        ind['obj_patches'].append(c)
                for i_obj, p in enumerate(ind['obj_patches']):
                    if i_obj < objs.shape[0]:
                        p.center = (objs[i_obj, 0], objs[i_obj, 1])
                    else:
                        # hide extra
                        p.center = (-1000, -1000)
                    artists.append(p)

            # append robot patches to artists
            for rp in ind.get('robot_patches', []):
                artists.append(rp)

        seconds = frame_idx // fps
        time_text.set_text(f"t = {seconds}s")
        artists.append(time_text)
        return artists

    anim = FuncAnimation(fig, update, frames=total_frames, interval=1000.0 / fps, blit=False)

    writer = FFMpegWriter(fps=fps, metadata={'artist': 'auto'}, bitrate=8000)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    anim.save(out_path, writer=writer, dpi=dpi)
    plt.close(fig)

def render_generation(generation):
    parser = argparse.ArgumentParser(description='Render 5x8 grid of clustering individuals to MP4')
    parser.add_argument('--dir', dest='base_dir', default=DEFAULT_BASE, help='Base run folder containing generation subfolders')
    parser.add_argument('--gen', dest='gen', type=int, default=generation, help='Generation index to read')
    filename = os.path.join(os.path.dirname(__file__), f'clustering_{generation}.mp4')
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