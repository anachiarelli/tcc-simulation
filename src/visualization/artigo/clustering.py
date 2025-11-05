"""Plot trajectories for generation 040 of the object_clustering run.

This script loads the best individual's position logs for generation 040
from the output/object_clustering/05-11-2025 19-29-50 run and creates a
single figure showing robot trajectories (underneath) and final positions
for robots (blue, diameter 7.2 cm) and objects (red, diameter 10 cm).

Saves image as `gen040_trajectories.png` inside the run folder.
"""
from __future__ import annotations

import os
import glob
from typing import Optional, Tuple, Sequence

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches


# Use an absolute path to the run folder (workspace root + output/...)
BASE_RUN = os.path.abspath(os.path.join(os.getcwd(), 'output', 'object_clustering', '05-11-2025 19-29-50'))

GEN = 100


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
    # kinds: 'robots' or 'objects' (subfolders inside positions/)
    dirp = os.path.join(gen_dir, 'positions', kind)
    if not os.path.isdir(dirp):
        return None
    prefix = f"{index:03d}_"
    # match any run suffix (_run0.csv .. _run9.csv) or any csv
    matches = glob.glob(os.path.join(dirp, prefix + "*" + "_run6.csv"))
    if not matches:
        print("hey")
        matches = glob.glob(os.path.join(dirp, prefix + "*.csv"))
    return matches[0] if matches else None


def load_robot_trajectory(pos_file: str) -> np.ndarray:
    """Load full robot trajectory from pos_file.

    Returns array shape (M, N, 3) where M time-steps and N robots.
    """
    return load_robot_trajectory_up_to(pos_file, None)


def load_robot_trajectory_up_to(pos_file: str, t: Optional[int]) -> np.ndarray:
    """Load robot trajectory up to timestamp t (inclusive).

    If t is None, loads all available lines. Returns array shape (M, N, 3)
    where M is number of time-steps read and N is number of robots. If no
    data, returns empty array with shape (0, 3).
    """
    if not os.path.exists(pos_file):
        return np.empty((0, 3))
    lines = []
    with open(pos_file, 'r') as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            parts = [p for p in line.strip().split(',') if p != '']
            vals = np.array([float(p) for p in parts])
            if vals.size % 3 != 0:
                vals = vals[: (vals.size // 3) * 3]
            if vals.size == 0:
                continue
            arr = vals.reshape((-1, 3))
            lines.append(arr)
            if t is not None and i >= t:
                break
    if not lines:
        return np.empty((0, 3))
    # ensure rectangular stack by trimming to minimum robot count per line
    min_n = min(l.shape[0] for l in lines)
    stacked = np.stack([l[:min_n, :] for l in lines], axis=0)
    return stacked


def load_objects_last_positions(pos_file: str) -> np.ndarray:
    """Load last available objects positions as (K,2) array.

    The objects file appears to store x,y pairs per object per line.
    """
    if not os.path.exists(pos_file):
        return np.empty((0, 2))
    last = None
    with open(pos_file, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            last = line.strip()
    if last is None:
        return np.empty((0, 2))
    parts = [p for p in last.split(',') if p != '']
    vals = np.array([float(p) for p in parts])
    if vals.size % 2 != 0:
        vals = vals[: (vals.size // 2) * 2]
    if vals.size == 0:
        return np.empty((0, 2))
    return vals.reshape((-1, 2))


def load_objects_positions_at(pos_file: str, t: Optional[int]) -> np.ndarray:
    """Load objects positions at timestamp t (0-based).

    If t is None, returns the last available line (same as previous function).
    Returns array shape (K,2) where K is number of objects.
    """
    if not os.path.exists(pos_file):
        return np.empty((0, 2))
    line_at = None
    with open(pos_file, 'r') as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            if t is None or i == t:
                line_at = line.strip()
                if t is not None and i == t:
                    break
    if line_at is None:
        return np.empty((0, 2))
    parts = [p for p in line_at.split(',') if p != '']
    vals = np.array([float(p) for p in parts])
    if vals.size % 2 != 0:
        vals = vals[: (vals.size // 2) * 2]
    if vals.size == 0:
        return np.empty((0, 2))
    return vals.reshape((-1, 2))


def plot(
    base_run: str = BASE_RUN,
    gen: int = GEN,
    arena_size: Tuple[float, float] = (112.0, 122.0),
    robot_diam_cm: float = 7.2,
    object_diam_cm: float = 10.0,
    timestamps: Sequence[int] = (0, 100, 200, 400, 1000, 1800),
    out_name: str = 'clustering-snapshots.png',
) -> str:
    gen_dir = os.path.join(base_run, f"{gen:03d}")
    if not os.path.isdir(gen_dir):
        raise SystemExit(f"Generation directory not found: {gen_dir}")

    fitness = read_fitness(gen_dir)
    if fitness is None or fitness.size == 0:
        raise SystemExit(f"No fitness.csv or empty under {gen_dir}")
    best_idx = int(np.argmax(fitness))

    robots_file = find_positions_file_for_index(gen_dir, best_idx, kind='robots')
    objects_file = find_positions_file_for_index(gen_dir, best_idx, kind='objects')
    if robots_file is None:
        raise SystemExit(f"No robot positions file found for index {best_idx} in {gen_dir}")
    # objects will be loaded per-timestamp so they match the robot frame
    # (we load inside the timestamps loop below)
    objs = None

    # build figure with one row and len(timestamps) columns
    cols = len(timestamps)
    figsize = (cols * 3.0, 3.0 * arena_size[1] / arena_size[0])
    fig, axes = plt.subplots(1, cols, figsize=figsize, squeeze=False)

    for c, t in enumerate(timestamps):
        ax = axes[0, c]
        # load trajectory up to timestamp t
        traj_t = load_robot_trajectory_up_to(robots_file, t)
        if traj_t.size == 0:
            ax.text(0.5, 0.5, 'no data', ha='center', va='center')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlim(0, arena_size[0])
            ax.set_ylim(0, arena_size[1])
            continue

        ax.set_aspect('equal')
        M, N, _ = traj_t.shape

        # plot per-robot continuous trajectories up to timestamp t (under)
        for i in range(N):
            xs = traj_t[:, i, 0]
            ys = traj_t[:, i, 1]
            ax.plot(xs, ys, color='tab:blue', alpha=0.4, linewidth=0.8, zorder=1)

        # plot objects positions at this timestamp on top of trajectories
        if objects_file:
            objs_at_t = load_objects_positions_at(objects_file, t)
        else:
            objs_at_t = np.empty((0, 2))
        for j in range(objs_at_t.shape[0]):
            x, y = objs_at_t[j]
            circ = patches.Circle((x, y), radius=object_diam_cm / 2.0, facecolor='red', edgecolor='k', linewidth=0.3, zorder=4)
            ax.add_patch(circ)

        # plot robots current positions (at timestamp t) above trajectories
        last = traj_t[-1]
        for i in range(last.shape[0]):
            x, y = last[i, 0], last[i, 1]
            circ = patches.Circle((x, y), radius=robot_diam_cm / 2.0, facecolor='tab:blue', edgecolor='k', linewidth=0.3, zorder=5)
            ax.add_patch(circ)

        ax.set_title(f"t={t}")
        ax.set_xlim(0, arena_size[0])
        ax.set_ylim(0, arena_size[1])
        ax.set_xticks([])
        ax.set_yticks([])

    # annotate left side with generation label on the y-axis (rotated)
    try:
        axes[0, 0].text(-0.12, 0.5, f"gen {gen}", transform=axes[0, 0].transAxes, rotation=90, va="center")
    except Exception:
        # if axes layout is different or something fails, silently ignore
        pass

    plt.tight_layout()

    # Save output into the artigo folder (same folder as this script) unless
    # an absolute path is provided.
    if os.path.isabs(out_name):
        out_path = out_name
    else:
        artigo_dir = os.path.dirname(__file__)
        out_path = os.path.join(artigo_dir, out_name)
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return out_path


if __name__ == '__main__':
    saved = plot()
    print(f"Saved image to: {saved}")
