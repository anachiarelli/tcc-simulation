#!/usr/bin/env python3
import csv
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import argparse
import numpy as np

# Default base dir can be overridden with --output-base
base_dir = Path('/home/anachiarelli/projects/udesc/tcc/simulation/output/sorting_objects/04-11-2025 03-11-07')


# Scenario constants (from src/Scenarios/sorting_objects/main.cpp)
SWARM_SIZE = 2
NUMBER_OF_GROUPS = 3
NUM_ROBOTS = SWARM_SIZE * NUMBER_OF_GROUPS  # 6
NUM_OBJECTS_PER_COLOR = 5
TOTAL_OBJECTS = NUM_OBJECTS_PER_COLOR * NUMBER_OF_GROUPS  # 15
DIAMETER_ROBOT = 7.4
DIAMETER_OBJECT = 10.0
WORLD_SIZE = 194.0

# Canonical colors (use same mapping used by other visualizers)
CANONICAL_COLORS = {
	'red': (1.0, 0.0, 0.0),
	'blue': (0.0, 0.45, 0.8),
	'green': (0.0, 0.7, 0.2)
}


def parse_id_from_filename(fname: str):
	try:
		base = os.path.basename(fname)
		tok = base.split('_', 1)[0]
		return int(tok)
	except Exception:
		return None


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


def read_robot_final_positions(pos_file: Path):
	"""Read robot CSV where each row contains 6 values per robot: x,y,theta,r,g,b.
	Return final_x, final_y, final_rgb lists of length NUM_ROBOTS.
	"""
	final_x = [0.0 for _ in range(NUM_ROBOTS)]
	final_y = [0.0 for _ in range(NUM_ROBOTS)]
	final_rgb = [None for _ in range(NUM_ROBOTS)]

	if not pos_file.is_file():
		return final_x, final_y, final_rgb

	last_vals = None
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
				last_vals = vals
	except Exception:
		last_vals = None

	if last_vals is None:
		return final_x, final_y, final_rgb

	for i in range(NUM_ROBOTS):
		base = 6 * i
		if base + 1 < len(last_vals):
			final_x[i] = last_vals[base]
			final_y[i] = last_vals[base + 1]
			if base + 5 < len(last_vals):
				r = last_vals[base + 3]
				g = last_vals[base + 4]
				b = last_vals[base + 5]
				if max(r, g, b) > 1.01:
					final_rgb[i] = (np.clip(r / 255.0, 0.0, 1.0), np.clip(g / 255.0, 0.0, 1.0), np.clip(b / 255.0, 0.0, 1.0))
				else:
					final_rgb[i] = (np.clip(r, 0.0, 1.0), np.clip(g, 0.0, 1.0), np.clip(b, 0.0, 1.0))

	return final_x, final_y, final_rgb


def read_objects_final_positions(pos_file: Path):
	"""Read object CSV where each row contains 5 values per object: x,y,r,g,b.
	Return final_x, final_y, final_rgb lists of length TOTAL_OBJECTS.
	"""
	final_x = [0.0 for _ in range(TOTAL_OBJECTS)]
	final_y = [0.0 for _ in range(TOTAL_OBJECTS)]
	final_rgb = [None for _ in range(TOTAL_OBJECTS)]

	if not pos_file.is_file():
		return final_x, final_y, final_rgb

	last_vals = None
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
				last_vals = vals
	except Exception:
		last_vals = None

	if last_vals is None:
		return final_x, final_y, final_rgb

	for i in range(TOTAL_OBJECTS):
		base = 5 * i
		if base + 1 < len(last_vals):
			final_x[i] = last_vals[base]
			final_y[i] = last_vals[base + 1]
			if base + 4 < len(last_vals):
				r = last_vals[base + 2]
				g = last_vals[base + 3]
				b = last_vals[base + 4]
				if max(r, g, b) > 1.01:
					final_rgb[i] = (np.clip(r / 255.0, 0.0, 1.0), np.clip(g / 255.0, 0.0, 1.0), np.clip(b / 255.0, 0.0, 1.0))
				else:
					final_rgb[i] = (np.clip(r, 0.0, 1.0), np.clip(g, 0.0, 1.0), np.clip(b, 0.0, 1.0))

	return final_x, final_y, final_rgb


def make_grid_for_generation(output_base: Path, generation: str, rows: int = 4, cols: int = 5, out_dir: Path = None):
	num_simulations = rows * cols
	generation_dir = output_base / generation
	robots_dir = generation_dir / 'positions' / 'robots'
	objects_dir = generation_dir / 'positions' / 'objects'

	if not robots_dir.is_dir():
		print(f"Robots positions directory not found under: {generation_dir}")
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
	fig_width = cols * 3.0
	fig_height = rows * 3.0
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
		ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
		ax.tick_params(left=True, bottom=True, labelleft=False, labelbottom=False)

		if sim_idx < len(ordered_ids):
			indiv_id = ordered_ids[sim_idx]
			robot_path = robots_dir / robots_map[indiv_id]
			# corresponding objects file uses the same filename but in the objects directory
			object_filename = robots_map[indiv_id]
			object_path = objects_dir / object_filename if (objects_dir.exists() and (objects_dir / object_filename).exists()) else None

			fval = None
			try:
				idx_in_list = next((i for i, (iid, _) in enumerate(id_fitness_list) if iid == indiv_id), None)
				if idx_in_list is not None:
					fval = id_fitness_list[idx_in_list][1]
			except Exception:
				fval = None

			title_text = f"Fitness = n/a"
			if fval is not None and not np.isnan(fval):
				try:
					title_text = f"Fitness = {fval:.2f}"
				except Exception:
					title_text = f"Fitness = {fval}"
			ax.set_title(title_text, fontsize=9, pad=6)

			rx, ry, rrgb = read_robot_final_positions(robot_path)
			ox, oy, orgb = ([], [], [])
			if object_path is not None and object_path.exists():
				ox, oy, orgb = read_objects_final_positions(object_path)

			is_best = (sim_idx == 0 and len(id_fitness_list_sorted) > 0 and not np.isnan(id_fitness_list_sorted[0][1]))

			# draw objects first (small, use object's own colors from CSV if available)
			for i in range(min(len(ox), TOTAL_OBJECTS)):
				x = ox[i]
				y = oy[i]
				if x is None:
					continue
				if orgb and orgb[i] is not None:
					color = orgb[i]
				else:
					color = CANONICAL_COLORS['blue']
				# lighter fill for objects (preserve recorded color and add alpha)
				obj_color = (color[0], color[1], color[2], 1.0)
				circle = Circle((x, y), DIAMETER_OBJECT / 2.0, facecolor=obj_color, edgecolor=('k'), linewidth=0.4)
				ax.add_patch(circle)

			# draw robots on top (solid, slightly larger)
			for i in range(min(len(rx), NUM_ROBOTS)):
				x = rx[i]
				y = ry[i]
				if x is None:
					continue
				color = nearest_canonical_color(rrgb[i]) if rrgb and rrgb[i] is not None else CANONICAL_COLORS['blue']
				# highlight robots of best individual
				edge = color
				circle = Circle((x, y), DIAMETER_ROBOT / 2.0, facecolor=color, edgecolor=edge, linewidth=0.8, alpha=1.0)
				ax.add_patch(circle)
		else:
			ax.set_title("individual n/a: Fitness = n/a", fontsize=9, pad=6)

	# save
	if out_dir is None:
		out_dir = Path.cwd()
	out_dir.mkdir(parents=True, exist_ok=True)
	out_path = out_dir / f'sorting_objects-snapshots-{generation}.png'
	fig.savefig(out_path, dpi=fig_dpi)
	plt.close(fig)
	print(f"Saved sorting_objects snapshots for generation {generation} -> {out_path}")
	return out_path


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--output-base', type=str, default=base_dir,
						help='Base output directory containing generation subfolders')
	parser.add_argument('--generations', type=str, default='704', help='Comma separated generation ids')
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
