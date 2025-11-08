
import csv
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import argparse
import numpy as np

# Constants taken from src/visualization/videos/grouping.py for visual consistency
NUM_ROBOTS = 10
DIAMETER_ROBOT = 7.4
WORLD_SIZE = 316  # cm
BLUE_COLOR = 'tab:blue'


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
			except ValueError:
				# ignore malformed lines
				fitnesses.append(float('nan'))
	return fitnesses


def read_final_positions(pos_file: Path):
	"""Read a positions CSV and return final x,y,theta lists for all robots.
	The CSV rows contain x,y,theta repeated for each robot per timestep.
	We return lists of length NUM_ROBOTS for x,y,theta (final frame or zeros if missing).
	"""
	xs = [[0.0] for _ in range(NUM_ROBOTS)]
	ys = [[0.0] for _ in range(NUM_ROBOTS)]
	thetas = [[0.0] for _ in range(NUM_ROBOTS)]
	if not pos_file.is_file():
		return [0.0] * NUM_ROBOTS, [0.0] * NUM_ROBOTS, [0.0] * NUM_ROBOTS

	last_valid = None
	try:
		with pos_file.open(newline='') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			for row in reader:
				# filter out empty strings and whitespace
				row = [value.strip() for value in row if value.strip()]
				if not row:
					continue
				try:
					rowf = [float(v) for v in row]
				except ValueError:
					# skip malformed rows
					continue
				last_valid = rowf
	except Exception:
		last_valid = None

	if last_valid is None:
		return [0.0] * NUM_ROBOTS, [0.0] * NUM_ROBOTS, [0.0] * NUM_ROBOTS

	final_x = []
	final_y = []
	final_theta = []
	for i in range(NUM_ROBOTS):
		base = 3 * i
		if base + 1 < len(last_valid):
			final_x.append(last_valid[base])
			final_y.append(last_valid[base + 1])
			if base + 2 < len(last_valid):
				final_theta.append(last_valid[base + 2])
			else:
				final_theta.append(0.0)
		else:
			final_x.append(0.0)
			final_y.append(0.0)
			final_theta.append(0.0)

	return final_x, final_y, final_theta


def make_grid_for_generation(output_base: Path, generation: str, rows: int = 5, cols: int = 8, out_dir: Path = None):
	"""Generate a rows x cols grid image with the final robot positions for the given generation.
	Saves the resulting PNG to out_dir or current working dir.
	"""
	num_simulations = rows * cols
	generation_dir = output_base / generation
	positions_dir = generation_dir / 'positions'
	if not positions_dir.is_dir():
		print(f"Positions directory not found: {positions_dir}")
		return None

	# select files similar to videos/grouping.py: files that end with '_1.csv'
	robot_files = [f for f in sorted(os.listdir(positions_dir)) if f.endswith('_1.csv')]
	robot_files = robot_files[:num_simulations]

	fitnesses = read_fitness(generation_dir)

	# Create an ordering of the selected robot files sorted by fitness (higher is better).
	# We assume fitnesses list aligns by index with the lexicographically sorted robot_files
	# If fitness is missing for a file, treat it as very low so it appears last.
	paired_count = len(robot_files)
	fvals = []
	for idx in range(paired_count):
		if idx < len(fitnesses):
			try:
				fvals.append(float(fitnesses[idx]))
			except Exception:
				fvals.append(float('nan'))
		else:
			fvals.append(float('nan'))

	# convert NaNs to very small numbers so they sort to the end
	farr = np.array(fvals, dtype=float) if fvals else np.array([], dtype=float)
	if farr.size > 0:
		farr_for_sort = np.nan_to_num(farr, nan=-np.inf)
		order = list(np.argsort(-farr_for_sort))
	else:
		order = []

	# Prepare figure
	fig_dpi = 100
	fig_width = cols * 2.0
	fig_height = rows * 2.0
	fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height), dpi=fig_dpi)
	axes = axes.flatten()

	# reduce whitespace between subplots so boxes are closer together
	plt.subplots_adjust(wspace=0.08, hspace=0.08)
	# reduce outer padding
	fig.tight_layout(h_pad=0.2, w_pad=0.8)

	for sim_idx in range(num_simulations):
		ax = axes[sim_idx]
		ax.clear()
		ax.set_xlim(0, WORLD_SIZE)
		ax.set_ylim(0, WORLD_SIZE)
		ax.set_aspect('equal')
		ax.grid(False)
		ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

		# map this subplot to the file index according to the fitness-sorted order
		if sim_idx < len(order):
			file_idx = order[sim_idx]
			pos_path = positions_dir / robot_files[file_idx]
			# title shows original individual index (file_idx) and its fitness if available
			fval = fvals[file_idx] if file_idx < len(fvals) else float('nan')
			title_text = f"Fitness = n/a"
			if not np.isnan(fval):
				try:
					title_text = f"f = {fval:.2f}"
				except Exception:
					title_text = f"f = {fval}"
			ax.set_title(title_text, fontsize=12, pad=8)

			xs, ys, thetas = read_final_positions(pos_path)
			# mark best (highest fitness) which is at sim_idx == 0 (if any fitness exists)
			is_best = False
			if farr.size > 0:
				# farr_for_sort was produced earlier; if the corresponding value is -inf it means NaN/missing
				if farr_for_sort[file_idx] != -np.inf and sim_idx == 0:
					is_best = True
			for i in range(min(len(xs), NUM_ROBOTS)):
				ind_color = BLUE_COLOR if is_best else BLUE_COLOR
				circle = Circle((xs[i], ys[i]), DIAMETER_ROBOT / 2.0, facecolor=ind_color, edgecolor='k', linewidth=0.5, alpha=0.95)
				ax.add_patch(circle)
		else:
			# no mapped file for this subplot
			ax.set_title(f"Indivíduo n/a:\nfitness = n/a", fontsize=9, pad=8)

	# Where to save
	if out_dir is None:
		out_dir = Path.cwd()
	out_dir.mkdir(parents=True, exist_ok=True)
	out_path = out_dir / f'comportamento-agregacao-{generation}.png'
	fig.savefig(out_path, dpi=fig_dpi)
	plt.close(fig)
	print(f"Saved snapshots for generation {generation} -> {out_path}")
	return out_path


def main():
	parser = argparse.ArgumentParser(description='Generate 5x8 grids of final robot positions for specified generations')
	parser.add_argument('--output-base', type=str, default='/home/anachiarelli/projects/udesc/tcc/simulation/output/grouping/20-10-2025 15-47-53',
						help='Base output directory (contains generation subfolders)')
	parser.add_argument('--generations', type=str, default='000,002,005,010,020,030,040,060,080,100',
						help='Comma separated list of generation names to plot (e.g. 000,050,100)')
	parser.add_argument('--rows', type=int, default=8, help='Grid rows (default 8)')
	parser.add_argument('--cols', type=int, default=5, help='Grid columns (default 5)')
	parser.add_argument('--out-dir', type=str, default=None, help='Directory to save snapshot images')

	args = parser.parse_args()

	output_base = Path(args.output_base)
	generations = [g.strip() for g in args.generations.split(',') if g.strip()]
	out_dir = Path(args.out_dir) if args.out_dir else None

	for generation in generations:
		make_grid_for_generation(output_base, generation, rows=args.rows, cols=args.cols, out_dir=out_dir)


if __name__ == '__main__':
	main()

