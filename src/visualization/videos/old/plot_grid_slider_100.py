import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import os
from matplotlib.widgets import Slider

num_robots = 30
num_objects = 7
diameter_robot = 0.074
diameter_object = 0.074
base_dir = '/home/anachiarelli/projects/udesc/tcc/simulation/output/object_clustering/02-10-2025 21-14-42/100/positions'
robots_dir = base_dir + '/robots'
objects_dir = base_dir + '/objects'
num_simulations = 100
rows, cols = 10, 10

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

num_frames = max(num_frames_all)

fig, axes = plt.subplots(rows, cols, figsize=(20, 20))
axes = axes.flatten()

robot_lines_all = []
robot_markers_all = []
robot_circles_all = []
object_lines_all = []
object_markers_all = []
object_circles_all = []

for sim_idx, ax in enumerate(axes):
    ax.set_xlim(0, 316)
    ax.set_ylim(0, 316)
    ax.set_aspect('equal')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    robot_lines = []
    robot_markers = []
    robot_circles = []
    object_lines = []
    object_markers = []
    object_circles = []
    if sim_idx < len(robot_files):
        for i in range(num_robots):
            line, = ax.plot([], [], color='blue', lw=0.5)
            marker, = ax.plot([], [], 'o', color='blue', markeredgecolor='black', markeredgewidth=1, markersize=4)
            circle = Circle((0, 0), diameter_robot, color='blue', edgecolor='black', linewidth=1, alpha=0.3)
            ax.add_patch(circle)
            robot_lines.append(line)
            robot_markers.append(marker)
            robot_circles.append(circle)
        for i in range(num_objects):
            line, = ax.plot([], [], color='purple', lw=0.5, linestyle='--')
            marker, = ax.plot([], [], 'o', color='purple', markersize=6)
            circle = Circle((0, 0), diameter_object, color='purple', alpha=0.3)
            ax.add_patch(circle)
            object_lines.append(line)
            object_markers.append(marker)
            object_circles.append(circle)
    robot_lines_all.append(robot_lines)
    robot_markers_all.append(robot_markers)
    robot_circles_all.append(robot_circles)
    object_lines_all.append(object_lines)
    object_markers_all.append(object_markers)
    object_circles_all.append(object_circles)

# Slider
ax_slider = fig.add_axes([0.2, 0.03, 0.6, 0.04], facecolor='lightgoldenrodyellow')
frame_slider = Slider(ax_slider, 'Frame', 0, num_frames - 1, valinit=0, valstep=1)

# Update function
def update(frame):
    for sim_idx, ax in enumerate(axes):
        if sim_idx < len(robot_files):
            robot_traj_x = robot_trajectories_x_all[sim_idx]
            robot_traj_y = robot_trajectories_y_all[sim_idx]
            object_traj_x = object_trajectories_x_all[sim_idx]
            object_traj_y = object_trajectories_y_all[sim_idx]
            num_frames_sim = num_frames_all[sim_idx]
            frame_idx = min(frame, num_frames_sim - 1)
            for i in range(num_robots):
                x = robot_traj_x[i]
                y = robot_traj_y[i]
                robot_lines_all[sim_idx][i].set_data(x[:frame_idx+1], y[:frame_idx+1])
                robot_markers_all[sim_idx][i].set_data(x[frame_idx], y[frame_idx])
                robot_circles_all[sim_idx][i].center = (x[frame_idx], y[frame_idx])
            for i in range(num_objects):
                x = object_traj_x[i]
                y = object_traj_y[i]
                object_lines_all[sim_idx][i].set_data(x[:frame_idx+1], y[:frame_idx+1])
                object_markers_all[sim_idx][i].set_data(x[frame_idx], y[frame_idx])
                object_circles_all[sim_idx][i].center = (x[frame_idx], y[frame_idx])
    fig.canvas.draw_idle()

frame_slider.on_changed(update)

fig.suptitle('Object Clustering(gen = 100 | mass = 75 | t = 1800 | pop = 100)', fontsize=14, y=0.94)
plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.2, rect=[0, 0, 1, 0.95])
plt.show()
