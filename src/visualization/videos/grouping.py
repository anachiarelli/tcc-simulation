import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import os
from matplotlib.animation import FuncAnimation, FFMpegWriter

# This script creates a video grid of simulations for the "grouping" scenario.
# Input CSV rows are expected to contain, for each robot, 3 consecutive values:
# x, y, theta
# Repeated for each robot: x,y,theta,x,y,theta,...
# All robots are drawn with the same blue color.

# Configuration (edit as needed)
num_robots = 10
diameter_robot = 7.4
world_size = 316  # in cm, should match simulation setup
generation = '100'
simulation_timestamp = '20-10-2025 03-45-27'

base_dir = '/home/anachiarelli/projects/udesc/tcc/simulation/output/grouping/' + simulation_timestamp + '/' + generation + '/positions'
num_simulations = 40
rows, cols = 4, 10

# Video parameters
fps = 10  # frames per second in output video

# Trajectory (trail) configuration
enable_trails = False # set to True to enable trails
trail_length = 40  # number of previous positions to draw (like plot_40)

#update this line, there is no ending with 0.csv, there is no such files
robot_files = [f for f in sorted(os.listdir(base_dir)) if f.endswith('_1.csv')][:num_simulations]

# Read all data
robot_trajectories_x_all = []
robot_trajectories_y_all = []
robot_trajectories_theta_all = []
num_frames_all = []

for robot_file in robot_files:
    robot_trajectories_x = [[] for _ in range(num_robots)]
    robot_trajectories_y = [[] for _ in range(num_robots)]
    robot_trajectories_theta = [[] for _ in range(num_robots)]
    with open(os.path.join(base_dir, robot_file), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            # filter out empty strings
            row = [value.strip() for value in row if value.strip()]
            # convert to floats
            try:
                rowf = [float(v) for v in row]
            except ValueError:
                # skip malformed rows
                continue
            # expect 3 values per robot: x,y,theta
            for i in range(num_robots):
                base = 3 * i
                if base + 2 < len(rowf):
                    x = rowf[base]
                    y = rowf[base + 1]
                    theta = rowf[base + 2]
                else:
                    # not enough values in this row for this robot, use last known or zeros
                    x = robot_trajectories_x[i][-1] if robot_trajectories_x[i] else 0.0
                    y = robot_trajectories_y[i][-1] if robot_trajectories_y[i] else 0.0
                    theta = robot_trajectories_theta[i][-1] if robot_trajectories_theta[i] else 0.0
                robot_trajectories_x[i].append(x)
                robot_trajectories_y[i].append(y)
                robot_trajectories_theta[i].append(theta)

    robot_trajectories_x_all.append(robot_trajectories_x)
    robot_trajectories_y_all.append(robot_trajectories_y)
    robot_trajectories_theta_all.append(robot_trajectories_theta)
    num_frames_all.append(len(robot_trajectories_x[0]))

total_sim_frames = max(num_frames_all) if num_frames_all else 0
video_frames = total_sim_frames

# Predefine a single blue color for all robots
blue_color = (0.0, 0.45, 0.8)  # pleasant blue

# Create Full HD figure (1920x1080). figsize is in inches; use 1920/100 x 1080/100 with dpi=100 for 1920x1080 pixels
fig_dpi = 100
fig_width = 1920 / fig_dpi
fig_height = 1080 / fig_dpi
fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height), dpi=fig_dpi)
axes = axes.flatten()

# Pre-create artists for each subplot to speed animation
plot_artists = []
for sim_idx, ax in enumerate(axes):
    ax.set_xlim(0, world_size)
    ax.set_ylim(0, world_size)
    ax.set_aspect('equal')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True, labelsize=8)
    ax.set_title(str(sim_idx), fontsize=12, pad=8, loc='center')
    artists = {'robot_circles': []}
    if enable_trails:
        artists['robot_trails'] = []
    if sim_idx < len(robot_files):
        for i in range(num_robots):
            circle = Circle((0, 0), diameter_robot / 2.0, facecolor=blue_color, edgecolor=blue_color, linewidth=1.0, alpha=0.95)
            ax.add_patch(circle)
            artists['robot_circles'].append(circle)
            if enable_trails:
                # create an initial empty Line2D for the robot's trail
                (line,) = ax.plot([], [], linewidth=1.2, color=blue_color, alpha=0.7)
                artists['robot_trails'].append(line)
    plot_artists.append(artists)

def update(frame):
    for sim_idx, ax in enumerate(axes):
        if sim_idx < len(robot_files):
            artists = plot_artists[sim_idx]
            for i in range(num_robots):
                xs = robot_trajectories_x_all[sim_idx][i]
                ys = robot_trajectories_y_all[sim_idx][i]
                idx = min(frame, len(xs) - 1)
                x_last = xs[idx]
                y_last = ys[idx]
                artists['robot_circles'][i].center = (x_last, y_last)
                # set uniform blue color
                artists['robot_circles'][i].set_facecolor(blue_color)
                artists['robot_circles'][i].set_edgecolor(blue_color)
                # update trail if enabled
                if enable_trails:
                    start_idx = max(0, idx - trail_length + 1)
                    trail_x = xs[start_idx:idx + 1]
                    trail_y = ys[start_idx:idx + 1]
                    artists['robot_trails'][i].set_data(trail_x, trail_y)
                    # fade the trail by adjusting alpha on the Line2D (matplotlib doesn't support per-segment alpha easily)
                    artists['robot_trails'][i].set_alpha(0.6)
    return []

ani = FuncAnimation(fig, update, frames=video_frames, blit=False)

output_file = os.path.join(os.path.dirname(__file__), 'grouping_' + generation + '.mp4')
try:
    writer = FFMpegWriter(fps=fps)
    ani.save(output_file, writer=writer, dpi=100)
    print(f"Saved video to {output_file}")
except Exception as e:
    print("Failed to save mp4 via FFMpegWriter. Make sure ffmpeg is installed and available in PATH.")
    print(str(e))
