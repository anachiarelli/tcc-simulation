import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import os

# --- Configuration (copy from plot_clustering.py as needed) ---
num_robots = 30
num_objects = 7
diameter_robot = 0.074
diameter_object = 0.074
base_dir = '/home/anachiarelli/projects/udesc/tcc/simulation/output/object_clustering/02-10-2025 15-33-51/001/positions'
robots_dir = base_dir + '/robots'
objects_dir = base_dir + '/objects'
num_simulations = 40
rows, cols = 5, 8

robot_files = [f for f in os.listdir(robots_dir)][:num_simulations]
object_files = [f for f in os.listdir(objects_dir)][:num_simulations]

robot_trajectories_x_all = []
robot_trajectories_y_all = []
object_trajectories_x_all = []
object_trajectories_y_all = []
num_frames_all = []

for robot_file, object_file in zip(robot_files, object_files):
    robot_trajectories_x = [[] for _ in range(num_robots)]
    robot_trajectories_y = [[] for _ in range(num_robots)]
    object_trajectories_x = [[] for _ in range(num_objects)]
    object_trajectories_y = [[] for _ in range(num_objects)]
    with open(os.path.join(robots_dir, robot_file), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            row = [float(value.strip()) for value in row if value.strip()]
            for i in range(num_robots):
                x = row[3 * i]
                y = row[3 * i + 1]
                robot_trajectories_x[i].append(x)
                robot_trajectories_y[i].append(y)
    with open(os.path.join(objects_dir, object_file), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            row = [float(value.strip()) for value in row if value.strip()]
            for i in range(num_objects):
                x = row[2 * i]
                y = row[2 * i + 1]
                object_trajectories_x[i].append(x)
                object_trajectories_y[i].append(y)
    robot_trajectories_x_all.append(robot_trajectories_x)
    robot_trajectories_y_all.append(robot_trajectories_y)
    object_trajectories_x_all.append(object_trajectories_x)
    object_trajectories_y_all.append(object_trajectories_y)
    num_frames_all.append(len(robot_trajectories_x[0]))

fig, axes = plt.subplots(rows, cols, figsize=(18, 8))
axes = axes.flatten()
for sim_idx, ax in enumerate(axes):
    ax.set_xlim(0, 316)
    ax.set_ylim(0, 316)
    ax.set_aspect('equal')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    if sim_idx < len(robot_files):
        # Robots
        for i in range(num_robots):
            x = robot_trajectories_x_all[sim_idx][i]
            y = robot_trajectories_y_all[sim_idx][i]
            ax.plot(x, y, color='blue', lw=0.5)
            ax.plot(x[-1], y[-1], 'o', color='blue', markeredgecolor='black', markeredgewidth=1, markersize=4)
            circle = Circle((x[-1], y[-1]), diameter_robot/2, color='blue', edgecolor='black', linewidth=1, alpha=0.3)
            ax.add_patch(circle)
        # Objects
        for i in range(num_objects):
            x = object_trajectories_x_all[sim_idx][i]
            y = object_trajectories_y_all[sim_idx][i]
            ax.plot(x, y, color='green', lw=0.5, linestyle='--')
            ax.plot(x[-1], y[-1], 's', color='green', markeredgecolor='black', markeredgewidth=1, markersize=6)
            circle = Circle((x[-1], y[-1]), diameter_object/2, color='green', edgecolor='black', linewidth=1, alpha=0.3)
            ax.add_patch(circle)
    else:
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1.5)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
# Add a title to the figure in the requested format
fig.suptitle('Object Clustering(gen = 01 | mass = 75 | t = 3600)', fontsize=14, y=0.94)
plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.2, rect=[0, 0, 1, 0.95])
# Save the figure in the same directory as this script
output_path = os.path.join(os.path.dirname(__file__), 'object_clustering_last_frame_gen01_mass75_t3600_h47.png')
fig.savefig(output_path, dpi=200)
plt.close(fig)
