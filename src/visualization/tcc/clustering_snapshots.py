import csv
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import argparse
import numpy as np

# Scenario-specific constants (from main.cpp and ClusteringEvaluator)
NUM_ROBOTS = 2
NUM_OBJECTS = 5
DIAMETER_ROBOT = 7.4
DIAMETER_OBJECT = 10.0
WORLD_SIZE = 112

# Colors
ROBOT_COLOR = 'tab:blue'  # blue
OBJECT_COLOR = 'tab:red'  # red
BEST_COLOR = 'tab:blue' 

def read_fitness(generation_dir: Path):
    fitness_file = generation_dir / 'fitness.csv'
    if not fitness_file.is_file():
        return []
    fitnesses = []
    with fitness_file.open() as f:
        for row in f:
            row = row.strip()
            if not row:
                continue
            try:
                fitnesses.append(float(row))
            except Exception:
                fitnesses.append(float('nan'))
    return fitnesses


def read_robot_trajectories(pos_file: Path):
    """Read robot CSV where each row contains 3 values per robot: x,y,theta."""
    robot_x = [[] for _ in range(NUM_ROBOTS)]
    robot_y = [[] for _ in range(NUM_ROBOTS)]
    robot_theta = [[] for _ in range(NUM_ROBOTS)]
    if not pos_file.is_file():
        return robot_x, robot_y, robot_theta
    try:
        with pos_file.open(newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                row = [v.strip() for v in row if v.strip()]
                if not row:
                    continue
                try:
                    vals = [float(v) for v in row]
                except Exception:
                    continue
                for i in range(NUM_ROBOTS):
                    base = 3 * i
                    if base + 1 < len(vals):
                        robot_x[i].append(vals[base])
                        robot_y[i].append(vals[base + 1])
                        robot_theta[i].append(vals[base + 2] if base + 2 < len(vals) else 0.0)
                    else:
                        # repeat last or 0
                        robot_x[i].append(robot_x[i][-1] if robot_x[i] else 0.0)
                        robot_y[i].append(robot_y[i][-1] if robot_y[i] else 0.0)
                        robot_theta[i].append(robot_theta[i][-1] if robot_theta[i] else 0.0)
    except Exception:
        pass
    return robot_x, robot_y, robot_theta


def read_object_trajectories(pos_file: Path):
    """Read object CSV where each row contains 2 values per object: x,y."""
    obj_x = [[] for _ in range(NUM_OBJECTS)]
    obj_y = [[] for _ in range(NUM_OBJECTS)]
    if not pos_file.is_file():
        return obj_x, obj_y
    try:
        with pos_file.open(newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                row = [v.strip() for v in row if v.strip()]
                if not row:
                    continue
                try:
                    vals = [float(v) for v in row]
                except Exception:
                    continue
                for i in range(NUM_OBJECTS):
                    base = 2 * i
                    if base + 1 < len(vals):
                        obj_x[i].append(vals[base])
                        obj_y[i].append(vals[base + 1])
                    else:
                        obj_x[i].append(obj_x[i][-1] if obj_x[i] else 0.0)
                        obj_y[i].append(obj_y[i][-1] if obj_y[i] else 0.0)
    except Exception:
        pass
    return obj_x, obj_y


def make_grid_for_generation(output_base: Path, generation: str, rows: int = 8, cols: int = 5, out_dir: Path = None):
    num_simulations = rows * cols
    generation_dir = output_base / generation
    robots_dir = generation_dir / 'positions' / 'robots'
    objects_dir = generation_dir / 'positions' / 'objects'
    if not robots_dir.is_dir() or not objects_dir.is_dir():
        print(f"Positions directories not found under: {generation_dir}")
        return None

    # collect all csv files and map them by individual id parsed from filename prefix
    robot_files_all = [f for f in os.listdir(robots_dir) if f.endswith('run2.csv')]
    object_files_all = [f for f in os.listdir(objects_dir) if f.endswith('run2.csv')]

    def parse_id_from_filename(fname: str):
        # expected filename format: 'NNN_<rest>.csv' where NNN is zero-padded individual id
        try:
            base = os.path.basename(fname)
            tok = base.split('_', 1)[0]
            return int(tok)
        except Exception:
            return None

    robots_map = {}
    for f in robot_files_all:
        iid = parse_id_from_filename(f)
        if iid is not None:
            robots_map[iid] = f

    objects_map = {}
    for f in object_files_all:
        iid = parse_id_from_filename(f)
        if iid is not None:
            objects_map[iid] = f

    # only consider individuals that have both robot and object files
    common_ids = sorted([iid for iid in robots_map.keys() if iid in objects_map])
    if not common_ids:
        print(f"No matching robot/object file pairs found in {generation_dir}")
        return None

    fitnesses = read_fitness(generation_dir)

    # build list of (id, fitness) for common ids
    id_fitness_list = []
    for iid in common_ids:
        if iid < len(fitnesses):
            try:
                sval = float(fitnesses[iid])
            except Exception:
                sval = float('nan')
        else:
            sval = float('nan')
        id_fitness_list.append((iid, sval))

    # sort by fitness descending, placing NaNs last
    def fitness_key(item):
        val = item[1]
        if np.isnan(val):
            return -np.inf
        return val

    id_fitness_list_sorted = sorted(id_fitness_list, key=lambda x: (np.isnan(x[1]), -x[1] if not np.isnan(x[1]) else 0.0))
    # produce ordered list of ids (best first)
    ordered_ids = [iid for iid, _ in id_fitness_list_sorted][:num_simulations]

    # prepare figure
    fig_dpi = 100
    fig_width = cols * 2.0
    fig_height = rows * 2.0
    fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height), dpi=fig_dpi)
    axes = axes.flatten()

    plt.subplots_adjust(wspace=0.06, hspace=0.06)
    fig.tight_layout(pad=0.6)

    for sim_idx in range(rows * cols):
        ax = axes[sim_idx]
        ax.clear()
        ax.set_xlim(0, WORLD_SIZE)
        ax.set_ylim(0, WORLD_SIZE)
        ax.set_aspect('equal')
        ax.grid(False)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)


        if sim_idx < len(ordered_ids):
            indiv_id = ordered_ids[sim_idx]
            robot_path = robots_dir / robots_map[indiv_id]
            object_path = objects_dir / objects_map[indiv_id]

            # title with original individual index and fitness
            fval = None
            try:
                # find fitness for this id in id_fitness_list (we built it earlier)
                idx_in_list = next((i for i, (iid, _) in enumerate(id_fitness_list) if iid == indiv_id), None)
                if idx_in_list is not None:
                    fval = id_fitness_list[idx_in_list][1]
            except Exception:
                fval = None
            title_text = f"f = n/a"
            if fval is not None and not np.isnan(fval):
                try:
                    title_text = f"f = {fval:.2f}"
                except Exception:
                    title_text = f"f = {fval}"
            ax.set_title(title_text, fontsize=12, pad=6)

            rx, ry, rtheta = read_robot_trajectories(robot_path)
            ox, oy = read_object_trajectories(object_path)

            # best is sim_idx == 0 because ordered_ids is sorted by fitness descending
            is_best = (sim_idx == 0 and len(id_fitness_list_sorted) > 0 and not np.isnan(id_fitness_list_sorted[0][1]))

            # plot robots: only final positions (no trajectories)
            for i in range(NUM_ROBOTS):
                xs = rx[i]
                ys = ry[i]
                if xs and ys:
                    color = ROBOT_COLOR
                    last_x, last_y = xs[-1], ys[-1]
                    circle = Circle((last_x, last_y), DIAMETER_ROBOT / 2.0, facecolor=color, edgecolor='k', linewidth=0.6, alpha=0.95)
                    ax.add_patch(circle)

            # plot objects: only final positions (no trajectories), colored red
            for i in range(NUM_OBJECTS):
                xs = ox[i]
                ys = oy[i]
                if xs and ys:
                    last_x, last_y = xs[-1], ys[-1]
                    circle = Circle((last_x, last_y), DIAMETER_OBJECT / 2.0, facecolor=OBJECT_COLOR, edgecolor='k', linewidth=0.8, alpha=0.9)
                    ax.add_patch(circle)
        else:
            ax.set_title("individual n/a: fitness = n/a", fontsize=9, pad=6)

    # save
    if out_dir is None:
        out_dir = Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'comportamento-clustering-{generation}.png'
    fig.savefig(out_path, dpi=fig_dpi)
    plt.close(fig)
    print(f"Saved clustering snapshots for generation {generation} -> {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-base', type=str, default='/home/anachiarelli/projects/udesc/tcc/simulation/output/object_clustering/06-11-2025 01-59-33',
                        help='Base output directory containing generation subfolders')
    parser.add_argument('--generations', type=str, default='000,002,005,010,020,030,040,060,080,100', help='Comma separated generation ids')
    parser.add_argument('--rows', type=int, default=8)
    parser.add_argument('--cols', type=int, default=5)
    parser.add_argument('--out-dir', type=str, default=None)
    args = parser.parse_args()

    output_base = Path(args.output_base)
    generations = [g.strip() for g in args.generations.split(',') if g.strip()]
    out_dir = Path(args.out_dir) if args.out_dir else None

    for generation in generations:
        make_grid_for_generation(output_base, generation, rows=args.rows, cols=args.cols, out_dir=out_dir)


if __name__ == '__main__':
    main()
