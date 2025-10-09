import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import numpy as np
import os
from matplotlib.animation import FuncAnimation, FFMpegWriter

# Configuration (copy from plot_last_frame_100.py as needed)
num_robots = 2
num_objects = 5
diameter_robot = 7.4
diameter_object = 10.0
world_size = 112  # in cm, should match simulation setup
generation = '000'

base_dir = '/home/anachiarelli/projects/udesc/tcc/simulation/output/object_clustering/08-10-2025 21-18-58/' + generation + '/positions'
robots_dir = base_dir + '/robots'
objects_dir = base_dir + '/objects'
num_simulations = 10
rows, cols = 2, 5

# Video parameters
fps = 10  # frames per second in output video
seconds_per_frame = 1  # how many seconds of simulation time correspond to one plotted frame

robot_files = [f for f in sorted(os.listdir(robots_dir)) if f.endswith('9.csv')][:num_simulations]
object_files = [f for f in sorted(os.listdir(objects_dir)) if f.endswith('9.csv')][:num_simulations]

# Read all data
robot_trajectories_x_all = []
robot_trajectories_y_all = []
robot_trajectories_theta_all = []
object_trajectories_x_all = []
object_trajectories_y_all = []
num_frames_all = []

for robot_file, object_file in zip(robot_files, object_files):
    robot_trajectories_x = [[] for _ in range(num_robots)]
    robot_trajectories_y = [[] for _ in range(num_robots)]
    robot_trajectories_theta = [[] for _ in range(num_robots)]
    object_trajectories_x = [[] for _ in range(num_objects)]
    object_trajectories_y = [[] for _ in range(num_objects)]
    with open(os.path.join(robots_dir, robot_file), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            row = [float(value.strip()) for value in row if value.strip()]
            for i in range(num_robots):
                x = row[3 * i]
                y = row[3 * i + 1]
                # third value is heading angle (radians or degrees depending on data)
                theta = row[3 * i + 2] if len(row) > 3 * i + 2 else 0.0
                robot_trajectories_x[i].append(x)
                robot_trajectories_y[i].append(y)
                # store theta trajectory
                robot_trajectories_theta[i].append(theta)
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
    # append collected theta trajectories
    robot_trajectories_theta_all.append(robot_trajectories_theta)
    object_trajectories_x_all.append(object_trajectories_x)
    object_trajectories_y_all.append(object_trajectories_y)
    num_frames_all.append(len(robot_trajectories_x[0]))

# Determine total frames to animate: use max number of frames across simulations
total_sim_frames = max(num_frames_all) if num_frames_all else 0

# Map simulation frames to video frames: if CSV rows correspond to 1Hz samples, then
# each simulation frame is one second. We will produce one video frame per simulation frame
# but allow fps>1 by duplicating frames (writer fps controls playback speed).
video_frames = total_sim_frames

# Create Full HD figure (1920x1080). figsize is in inches; use 1920/100 x 1080/100 with dpi=100 for 1920x1080 pixels
fig_dpi = 100
fig_width = 1920 / fig_dpi
fig_height = 1080 / fig_dpi
fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height), dpi=fig_dpi)
axes = axes.flatten()

# Pre-create artists for each subplot to speed animation
plot_artists = []
for sim_idx, ax in enumerate(axes):
    # axis limits are in centimeters
    ax.set_xlim(0, world_size)
    ax.set_ylim(0, world_size)
    ax.set_aspect('equal')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    # show tick labels so user can see axis values
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True, labelsize=8)
    # Add a numeric label above each subplot (0,1,2...)
    ax.set_title(str(sim_idx), fontsize=12, pad=8, loc='center')
    # placeholder lists for artists per subplot
    artists = {'robot_lines': [], 'robot_dots': [], 'robot_circles': [],
               'object_lines': [], 'object_dots': [], 'object_circles': [], 'robot_arrows': []}
    if sim_idx < len(robot_files):
        # create artists: path lines and Circle patches sized in cm
        for i in range(num_robots):
            # robot path and appearance: dark blue for robot marker/path, light blue for arrow
            robot_color = '#0b3d91'  # darker blue for robot (deep/navy)
            arrow_color = '#4da6ff'  # lighter blue for heading arrow
            line, = ax.plot([], [], color=robot_color, lw=1.0)
            # Circle radius in data units (cm): diameter_robot/2
            # fill robot circle with the robot_color so robot marker is dark blue (not white)
            circle = Circle((0, 0), diameter_robot / 2.0, facecolor=robot_color, edgecolor=robot_color, linewidth=1.2, alpha=1.0)
            ax.add_patch(circle)
            artists['robot_lines'].append(line)
            artists['robot_circles'].append(circle)
            # create a small arrow to indicate heading; initial arrow points to the right
            # arrow length in cm (visual only)
            # make the arrow slightly longer and use a lighter blue
            arrow_len = diameter_robot * 1.6
            # FancyArrowPatch uses (x, y) for start and (x2, y2) for end
            arrow = FancyArrowPatch((0, 0), (arrow_len, 0), color=arrow_color, linewidth=1.4, arrowstyle='-|>', mutation_scale=16)
            ax.add_patch(arrow)
            artists['robot_arrows'].append(arrow)
        for i in range(num_objects):
            line, = ax.plot([], [], color='red', lw=0.8, linestyle='--', alpha=0.5)
            circle = Circle((0, 0), diameter_object / 2.0, facecolor='red', edgecolor='darkred', linewidth=1.0, alpha=0.9)
            ax.add_patch(circle)
            artists['object_lines'].append(line)
            artists['object_circles'].append(circle)
    plot_artists.append(artists)

def get_position_or_last(data_list, frame_idx):
    # return value at frame_idx or last available if out of range
    if frame_idx < len(data_list):
        return data_list[frame_idx]
    return data_list[-1]

def update(frame):
    # frame is simulation frame index (per-second)
    for sim_idx, ax in enumerate(axes):
        if sim_idx < len(robot_files):
            artists = plot_artists[sim_idx]
            # robots
            for i in range(num_robots):
                xs = robot_trajectories_x_all[sim_idx][i]
                ys = robot_trajectories_y_all[sim_idx][i]
                thetas = robot_trajectories_theta_all[sim_idx][i]
                # build path up to this frame (or last available)
                idx = min(frame, len(xs) - 1)
                artists['robot_lines'][i].set_data(xs[:idx + 1], ys[:idx + 1])
                x_last = xs[idx]
                y_last = ys[idx]
                # update Circle center
                artists['robot_circles'][i].center = (x_last, y_last)
                # update arrow to point in heading direction
                # get theta (if available) or use 0
                if len(thetas) > idx:
                    theta = thetas[idx]
                else:
                    theta = thetas[-1] if thetas else 0.0
                # arrow length (slightly longer to be more visible)
                arrow_len = diameter_robot * 1.0
                dx = arrow_len * np.cos(theta)
                dy = arrow_len * np.sin(theta)
                # set new arrow positions: from center to (center + (dx,dy))
                artists['robot_arrows'][i].set_positions((x_last, y_last), (x_last + dx, y_last + dy))
            # objects
            for i in range(num_objects):
                xs = object_trajectories_x_all[sim_idx][i]
                ys = object_trajectories_y_all[sim_idx][i]
                idx = min(frame, len(xs) - 1)
                artists['object_lines'][i].set_data(xs[:idx + 1], ys[:idx + 1])
                x_last = xs[idx]
                y_last = ys[idx]
                # update Circle center
                artists['object_circles'][i].center = (x_last, y_last)
    return []

ani = FuncAnimation(fig, update, frames=video_frames, blit=False)

# Check ffmpeg availability when saving
output_file = os.path.join(os.path.dirname(__file__), 'object_clustering_mutation_1_' + generation + '.mp4')
try:
    writer = FFMpegWriter(fps=fps)
    ani.save(output_file, writer=writer, dpi=100)
    print(f"Saved video to {output_file}")
except Exception as e:
    print("Failed to save mp4 via FFMpegWriter. Make sure ffmpeg is installed and available in PATH.")
    print(str(e))
