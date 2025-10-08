import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import numpy as np
import os
from matplotlib.widgets import Slider

num_robots = 30
num_objects = 7
diameter_robot = 0.074
diameter_object = 0.074
interpolations_per_frame = 1
base_dir = '/home/anachiarelli/projects/udesc/tcc/simulation/output/object_clustering/02-10-2025 15-33-51/000/positions'
robots_dir = base_dir + '/robots'
objects_dir = base_dir + '/objects'
num_simulations = 40
rows, cols = 5, 8 # Grid Layout (5x8 = 40)

# robots files format: (x, y, angle), (x, y, angle), ...
# objects files format: (x, y), (x, y), ...

# plot robots and objects trajectories from multiple simulations in a grid layout
# robots must be blue circles and objects must be red circles
# there's one simulation per file

# List of files in the directory
robot_files = [f for f in os.listdir(robots_dir)]
robot_files = robot_files[:num_simulations]  # Limit to num_simulations files
object_files = [f for f in os.listdir(objects_dir)]
object_files = object_files[:num_simulations]  # Limit to num_simulations files

# Initialize lists to store trajectories of all simulations
robot_trajectories_x_interp_all = []
robot_trajectories_y_interp_all = []
object_trajectories_x_interp_all = []
object_trajectories_y_interp_all = []
num_frames_all = []

# Process each file
for robot_file, object_file in zip(robot_files, object_files):
    robot_trajectories_x_raw = [[] for _ in range(num_robots)]
    robot_trajectories_y_raw = [[] for _ in range(num_robots)]
    object_trajectories_x_raw = [[] for _ in range(num_objects)]
    object_trajectories_y_raw = [[] for _ in range(num_objects)]

    # Read robot file
    with open(os.path.join(robots_dir, robot_file), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            row = [float(value.strip()) for value in row if value.strip()]
            for i in range(num_robots):
                x = row[3 * i]
                y = row[3 * i + 1]
                robot_trajectories_x_raw[i].append(x)
                robot_trajectories_y_raw[i].append(y)

    # Read object file
    with open(os.path.join(objects_dir, object_file), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            row = [float(value.strip()) for value in row if value.strip()]
            for i in range(num_objects):
                x = row[2 * i]
                y = row[2 * i + 1]
                object_trajectories_x_raw[i].append(x)
                object_trajectories_y_raw[i].append(y)

    # Linear interpolation
    robot_trajectories_x_interp = []
    robot_trajectories_y_interp = []
    object_trajectories_x_interp = []
    object_trajectories_y_interp = []

    for i in range(num_robots):
        x = np.array(robot_trajectories_x_raw[i])
        y = np.array(robot_trajectories_y_raw[i])
        x_interp = []
        y_interp = []

        for j in range(len(x) - 1):
            x_steps = np.linspace(x[j], x[j+1], interpolations_per_frame, endpoint=False)
            y_steps = np.linspace(y[j], y[j+1], interpolations_per_frame, endpoint=False)
            x_interp.extend(x_steps)
            y_interp.extend(y_steps)

        x_interp.append(x[-1])
        y_interp.append(y[-1])

        robot_trajectories_x_interp.append(x_interp)
        robot_trajectories_y_interp.append(y_interp)

    for i in range(num_objects):
        x = np.array(object_trajectories_x_raw[i])
        y = np.array(object_trajectories_y_raw[i])
        x_interp = []
        y_interp = []

        for j in range(len(x) - 1):
            x_steps = np.linspace(x[j], x[j+1], interpolations_per_frame, endpoint=False)
            y_steps = np.linspace(y[j], y[j+1], interpolations_per_frame, endpoint=False)
            x_interp.extend(x_steps)
            y_interp.extend(y_steps)

        x_interp.append(x[-1])
        y_interp.append(y[-1])

        object_trajectories_x_interp.append(x_interp)
        object_trajectories_y_interp.append(y_interp)

    robot_trajectories_x_interp_all.append(robot_trajectories_x_interp)
    robot_trajectories_y_interp_all.append(robot_trajectories_y_interp)
    object_trajectories_x_interp_all.append(object_trajectories_x_interp)
    object_trajectories_y_interp_all.append(object_trajectories_y_interp)
    num_frames_all.append(len(robot_trajectories_x_interp[0]))

# Determine the maximum number of frames among all simulations
num_frames = max(num_frames_all)

fig, axes = plt.subplots(rows, cols, figsize=(18, 8))  # 1920x1080 pixels at 100 DPI
axes = axes.flatten()  # Eases access to subplots
# Reserve space at the bottom for the slider
fig.subplots_adjust(bottom=0.12)
robot_colors = lambda i: 'blue'
object_colors = lambda i: 'red'

# Initialize lists to store graphic elements
robot_lines_all = []
robot_markers_all = []
robot_circles_all = []
object_lines_all = []
object_markers_all = []
object_circles_all = []

# Configure each subplot
for ax in axes:
    ax.set_xlim(-1, 1)
    ax.set_ylim(-0.5, 1.5)
    ax.set_aspect('equal', 'box')
    # Show all spines (borders)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# Add slider for frame control in a dedicated space below the plots
ax_slider = fig.add_axes([0.2, 0.03, 0.6, 0.04], facecolor='lightgoldenrodyellow')
frame_slider = Slider(ax_slider, 'Frame', 0, num_frames - 1, valinit=0, valstep=1)

# Configure each subplot
for sim_idx, ax in enumerate(axes):
    if sim_idx < len(robot_files):
        ax.set_xlim(0, 316)
        ax.set_ylim(0, 316)
        ax.grid(True)
        ax.set_aspect('equal')
        ax.set_title(f'{sim_idx+1}', fontsize=10)
        ax.tick_params(labelsize=5)

        # Robots
        robot_lines = []
        robot_markers = []
        robot_circles = []
        for i in range(num_robots):
            line, = ax.plot([], [], color='blue', lw=0.5)
            marker, = ax.plot([], [], 'o', color='blue', markeredgecolor='black', markeredgewidth=1, markersize=4)
            circle = Circle((0, 0), diameter_robot/2, color='blue', edgecolor='black', linewidth=1, alpha=0.3)
            ax.add_patch(circle)
            robot_lines.append(line)
            robot_markers.append(marker)
            robot_circles.append(circle)
        robot_lines_all.append(robot_lines)
        robot_markers_all.append(robot_markers)
        robot_circles_all.append(robot_circles)

        # Objects
        object_lines = []
        object_markers = []
        object_circles = []
        for i in range(num_objects):
            line, = ax.plot([], [], color='red', lw=0.5, linestyle='--')
            marker, = ax.plot([], [], 's', color='red', markeredgecolor='black', markeredgewidth=1, markersize=6)
            circle = Circle((0, 0), diameter_object/2, color='red', edgecolor='black', linewidth=1, alpha=0.3)
            ax.add_patch(circle)
            object_lines.append(line)
            object_markers.append(marker)
            object_circles.append(circle)
        object_lines_all.append(object_lines)
        object_markers_all.append(object_markers)
        object_circles_all.append(object_circles)
    else:
        # Show borders and grid for unused subplots too
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1.5)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# Update function for animation
def update(frame):
    elements = []
    for sim_idx, ax in enumerate(axes):
        if sim_idx < len(robot_files):
            robot_traj_x = robot_trajectories_x_interp_all[sim_idx]
            robot_traj_y = robot_trajectories_y_interp_all[sim_idx]
            object_traj_x = object_trajectories_x_interp_all[sim_idx]
            object_traj_y = object_trajectories_y_interp_all[sim_idx]
            num_frames_sim = num_frames_all[sim_idx]
            frame_idx = min(frame, num_frames_sim - 1)  # Avoid out-of-bounds

            # Update robots
            for i in range(num_robots):
                x = robot_traj_x[i]
                y = robot_traj_y[i]
                robot_lines_all[sim_idx][i].set_data(x[:frame_idx+1], y[:frame_idx+1])
                robot_markers_all[sim_idx][i].set_data(x[frame_idx], y[frame_idx])
                robot_circles_all[sim_idx][i].center = (x[frame_idx], y[frame_idx])
                elements.extend([robot_lines_all[sim_idx][i], robot_markers_all[sim_idx][i], robot_circles_all[sim_idx][i]])

            # Update objects
            for i in range(num_objects):
                x = object_traj_x[i]
                y = object_traj_y[i]
                object_lines_all[sim_idx][i].set_data(x[:frame_idx+1], y[:frame_idx+1])
                object_markers_all[sim_idx][i].set_data(x[frame_idx], y[frame_idx])
                object_circles_all[sim_idx][i].center = (x[frame_idx], y[frame_idx])
                elements.extend([object_lines_all[sim_idx][i], object_markers_all[sim_idx][i], object_circles_all[sim_idx][i]])

    return elements

# Slider update function
def slider_update(val):
    frame = int(frame_slider.val)
    update(frame)
    plt.draw()

frame_slider.on_changed(slider_update)

# Adjust layout to minimize margins
plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.2)  # Reduce spacing between subplots
plt.show()