import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import os

# --- Configuration (copy from plot_clustering.py as needed) ---
num_robots = 2
num_objects = 5
diameter_robot = 7.4
diameter_object = 10.0
base_dir = '/home/anachiarelli/projects/udesc/tcc/simulation/output/object_clustering/08-10-2025 16-19-29/999/positions'
robots_dir = base_dir + '/robots'
objects_dir = base_dir + '/objects'
num_simulations = 10
rows, cols = 2, 5

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

fig, axes = plt.subplots(rows, cols, figsize=(20, 20))
axes = axes.flatten()
for sim_idx, ax in enumerate(axes):
    ax.set_xlim(0, 112)
    ax.set_ylim(0, 112)
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
            ax.plot(x[-1], y[-1], 'o', color='black', markeredgecolor='black', markersize=diameter_robot)
            circle = Circle((x[-1], y[-1]), diameter_robot, color='blue', edgecolor='blue', linewidth=1, alpha=0.3)
            ax.add_patch(circle)
        # Objects
        for i in range(num_objects):
            x = object_trajectories_x_all[sim_idx][i]
            y = object_trajectories_y_all[sim_idx][i]
            ax.plot(x, y, color='red', lw=0.5, linestyle='--')
            ax.plot(x[-1], y[-1], 'o', color='red', markersize=diameter_object)
            circle = Circle((x[-1], y[-1]), diameter_object, color='red', alpha=0.3)
            ax.add_patch(circle)
            ax.add_patch(circle)
    else:
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1.5)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
# Add a title to the figure in the requested format
fig.suptitle('Object Clustering(gen = 999)')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
# Save the figure in the same directory as this script
output_path = os.path.join(os.path.dirname(__file__), 'object_clustering_last_frame_gen999.png')
fig.savefig(output_path, dpi=200)
plt.close(fig)
