import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import os
from matplotlib.animation import FuncAnimation, FFMpegWriter

"""
plot_frames_video_run0.py

Duplicate of plot_frames_video_gen999.py but only includes files that end with
run_0.csv (i.e. the first run for each individual). Change `run_index` below
to include a different run (e.g. 1 for run_1.csv).

Place this file next to the original and run it to generate the MP4.
"""

# Configuration (mirrors the original script)
num_robots = 2
num_objects = 5
diameter_robot = 7.4
diameter_object = 10.0
base_dir = '/home/anachiarelli/projects/udesc/tcc/simulation/output/object_clustering/08-10-2025 17-46-37/080/positions'
robots_dir = base_dir + '/robots'
objects_dir = base_dir + '/objects'
num_simulations = 10
rows, cols = 2, 5

# Which run index to include in the video (0 -> run_0.csv)
run_index = 0

# Video parameters
fps = 10  # frames per second in output video
seconds_per_frame = 1  # how many seconds of simulation time correspond to one plotted frame

# helper to accept filenames that end with run_n.csv
def filter_run_files(files, prefix_filter=None):
    # files: list of filenames
    # prefix_filter: if provided, ensures filename contains this prefix before run
    run_suffix = f"run_{run_index}.csv"
    selected = [f for f in sorted(files) if f.endswith(run_suffix)]
    return selected[:num_simulations]

robot_files = filter_run_files(os.listdir(robots_dir))
object_files = filter_run_files(os.listdir(objects_dir))

# Read all data
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

# Determine total frames to animate: use max number of frames across simulations
total_sim_frames = max(num_frames_all) if num_frames_all else 0

# Map simulation frames to video frames
video_frames = total_sim_frames

fig, axes = plt.subplots(rows, cols, figsize=(20, 20))
axes = axes.flatten()

# Pre-create artists for each subplot to speed animation
plot_artists = []
for sim_idx, ax in enumerate(axes):
    # axis limits are in centimeters
    ax.set_xlim(0, 112)
    ax.set_ylim(0, 112)
    ax.set_aspect('equal')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    # placeholder lists for artists per subplot
    artists = {'robot_lines': [], 'robot_dots': [], 'robot_circles': [],
               'object_lines': [], 'object_dots': [], 'object_circles': []}
    if sim_idx < len(robot_files):
        # create artists: path lines and Circle patches sized in cm
        for i in range(num_robots):
            line, = ax.plot([], [], color='blue', lw=0.5)
            circle = Circle((0, 0), diameter_robot / 2.0, facecolor='black', edgecolor='blue', linewidth=1.0, alpha=1.0)
            ax.add_patch(circle)
            artists['robot_lines'].append(line)
            artists['robot_circles'].append(circle)
        for i in range(num_objects):
            line, = ax.plot([], [], color='red', lw=0.5, linestyle='--')
            circle = Circle((0, 0), diameter_object / 2.0, facecolor='red', edgecolor='red', linewidth=1.0, alpha=1.0)
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
                # build path up to this frame (or last available)
                idx = min(frame, len(xs) - 1)
                artists['robot_lines'][i].set_data(xs[:idx + 1], ys[:idx + 1])
                x_last = xs[idx]
                y_last = ys[idx]
                # update Circle center
                artists['robot_circles'][i].center = (x_last, y_last)
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
output_file = os.path.join(os.path.dirname(__file__), f'MEAN_VALUE_object_clustering_run{run_index}_gen080.mp4')
try:
    writer = FFMpegWriter(fps=fps)
    ani.save(output_file, writer=writer, dpi=100)
    print(f"Saved video to {output_file}")
except Exception as e:
    print("Failed to save mp4 via FFMpegWriter. Make sure ffmpeg is installed and available in PATH.")
    print(str(e))
