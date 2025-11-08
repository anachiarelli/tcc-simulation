import csv
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import argparse
import numpy as np

base_dir = Path('/home/anachiarelli/projects/udesc/tcc/simulation/output/sorting_groups/31-10-2025 02-14-17')
# base_dir = Path('/home/anachiarelli/projects/udesc/tcc/simulation/output/sorting_groups/31-10-2025 05-49-53')

# Scenario-specific constants (from src/Scenarios/sorting_groups/main.cpp)
NUM_ROBOTS = 30
DIAMETER_ROBOT = 7.4
WORLD_SIZE = 450

# Canonical colors requested: red, blue, green
CANONICAL_COLORS = {
    'red': (1.0, 0.0, 0.0),
    'blue': (0.0, 0.45, 0.8),
    'green': (0.0, 0.7, 0.2)
}

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
                fitnesses.append(float(row) * 100)
            except Exception:
                fitnesses.append(float('nan'))
    return fitnesses


def read_robot_final_positions(pos_file: Path):
    """Read robot CSV where each row contains 6 values per robot: x,y,theta,r,g,b.
    Returns lists final_x, final_y and final_rgb tuples (r,g,b normalized to [0,1] if present).
    """
    final_x = [0.0 for _ in range(NUM_ROBOTS)]
    final_y = [0.0 for _ in range(NUM_ROBOTS)]
    final_rgb = [None for _ in range(NUM_ROBOTS)]

    if not pos_file.is_file():
        return final_x, final_y, final_rgb

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
                    base = 6 * i
                    if base + 1 < len(vals):
                        final_x[i] = vals[base]
                        final_y[i] = vals[base + 1]
                        # read rgb if available
                        if base + 5 < len(vals):
                            r = vals[base + 3]
                            g = vals[base + 4]
                            b = vals[base + 5]
                            # normalize: if values appear >1 assume 0-255
                            if max(r, g, b) > 1.01:
                                final_rgb[i] = (np.clip(r / 255.0, 0.0, 1.0), np.clip(g / 255.0, 0.0, 1.0), np.clip(b / 255.0, 0.0, 1.0))
                            else:
                                final_rgb[i] = (np.clip(r, 0.0, 1.0), np.clip(g, 0.0, 1.0), np.clip(b, 0.0, 1.0))
                    # else keep previous / default
    except Exception:
        pass
    return final_x, final_y, final_rgb


def nearest_canonical_color(rgb):
    if rgb is None:
        return CANONICAL_COLORS['blue']
    best_name = None
    best_dist = float('inf')
    for name, cref in CANONICAL_COLORS.items():
        d = (rgb[0] - cref[0]) ** 2 + (rgb[1] - cref[1]) ** 2 + (rgb[2] - cref[2]) ** 2
        if d < best_dist:
            best_dist = d
            best_name = name
    return CANONICAL_COLORS[best_name]


def parse_id_from_filename(fname: str):
    try:
        base = os.path.basename(fname)
        tok = base.split('_', 1)[0]
        return int(tok)
    except Exception:
        return None


def make_grid_for_generation(output_base: Path, generation: str, rows: int = 8, cols: int = 5, out_dir: Path = None):
    num_simulations = rows * cols
    generation_dir = output_base / generation
    robots_dir = generation_dir / 'positions' / 'robots'
    if not robots_dir.is_dir():
        print(f"Positions directory not found under: {generation_dir}")
        return None

    robot_files_all = [f for f in os.listdir(robots_dir) if f.endswith('0.csv')]
    robots_map = {}
    for f in robot_files_all:
        iid = parse_id_from_filename(f)
        if iid is not None:
            robots_map[iid] = f

    if not robots_map:
        print(f"No robot files found in {robots_dir}")
        return None

    common_ids = sorted(robots_map.keys())

    fitnesses = read_fitness(generation_dir)

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

    # sort by fitness descending, NaNs last
    id_fitness_list_sorted = sorted(id_fitness_list, key=lambda x: (np.isnan(x[1]), -x[1] if not np.isnan(x[1]) else 0.0))
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

            fval = None
            try:
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

            rx, ry, rrgb = read_robot_final_positions(robot_path)

            # best is sim_idx == 0 because ordered_ids is sorted by fitness descending
            is_best = (sim_idx == 0 and len(id_fitness_list_sorted) > 0 and not np.isnan(id_fitness_list_sorted[0][1]))

            for i in range(NUM_ROBOTS):
                x = rx[i]
                y = ry[i]
                if x is None:
                    continue
                # determine color: map recorded rgb to nearest canonical color; if missing, use black
                if rrgb[i] is not None:
                    color = nearest_canonical_color(rrgb[i])
                else:
                    color = 'black'

                circle = Circle((x, y), DIAMETER_ROBOT / 2.0, facecolor=color, edgecolor='k', linewidth=0.2, alpha=0.95)
                ax.add_patch(circle)
        else:
            ax.set_title("individual n/a: Fitness = n/a", fontsize=9, pad=6)

    # save
    if out_dir is None:
        out_dir = Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'comportamento-multitask-{generation}.png'
    fig.savefig(out_path, dpi=fig_dpi)
    plt.close(fig)
    print(f"Saved sorting snapshots for generation {generation} -> {out_path}")
    return out_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-base', type=str, default=base_dir,
                        help='Base output directory containing generation subfolders')
    parser.add_argument('--generations', type=str, default='100', help='Comma separated generation ids')
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
