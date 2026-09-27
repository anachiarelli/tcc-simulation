import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import os
from matplotlib.animation import FuncAnimation, FFMpegWriter

# This script is based on clustering.py but assumes there are no objects.
# Robot CSV rows are expected to contain, for each robot, 6 consecutive values:
# x, y, theta, r, g, b
# where r,g,b are integers in the range 0-255. If your data uses 0-1 floats,
# set `rgb_0_255 = False` below.

# Configuration
num_robots = 30
diameter_robot = 7.4
world_size = 450  # in cm, should match simulation setup
generation = '200'
simulation_timestamp = '12-10-2025 15-23-11'

base_dir = '/home/anachiarelli/projects/udesc/tcc/simulation/output/sorting_groups/' + simulation_timestamp + '/' + generation + '/positions'
robots_dir = base_dir + '/robots'
num_simulations = 10
rows, cols = 2, 5

# Video parameters
fps = 10  # frames per second in output video

# If your RGB values are integers 0-255 set True, else False for 0-1 floats
# Default to False because your data uses 0-1 values. Set to True to force 0-255
# If rgb_detect is True (default) the script will inspect the data and override
# this value automatically.
rgb_0_255 = False
# Enable auto-detection of RGB range (will override rgb_0_255 if True)
rgb_detect = True

robot_files = [f for f in sorted(os.listdir(robots_dir)) if f.endswith('0.csv')][:num_simulations]

# Read all data
robot_trajectories_x_all = []
robot_trajectories_y_all = []
robot_trajectories_theta_all = []
robot_trajectories_rgb_all = []  # per-robot RGB per frame
num_frames_all = []

for robot_file in robot_files:
    robot_trajectories_x = [[] for _ in range(num_robots)]
    robot_trajectories_y = [[] for _ in range(num_robots)]
    robot_trajectories_theta = [[] for _ in range(num_robots)]
    robot_trajectories_rgb = [[[] for _ in range(num_robots)] for __ in range(3)]  # r,g,b lists per robot
    with open(os.path.join(robots_dir, robot_file), newline='') as csvfile:
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
            # expect 6 values per robot: x,y,theta,r,g,b
            for i in range(num_robots):
                base = 6 * i
                if base + 5 < len(rowf):
                    x = rowf[base]
                    y = rowf[base + 1]
                    theta = rowf[base + 2]
                    r = rowf[base + 3]
                    g = rowf[base + 4]
                    b = rowf[base + 5]
                else:
                    # not enough values in this row for this robot, use last known or zeros
                    # this keeps CSVs with fewer columns from crashing
                    x = robot_trajectories_x[i][-1] if robot_trajectories_x[i] else 0.0
                    y = robot_trajectories_y[i][-1] if robot_trajectories_y[i] else 0.0
                    theta = robot_trajectories_theta[i][-1] if robot_trajectories_theta[i] else 0.0
                    r, g, b = (0.0, 0.0, 0.0)
                robot_trajectories_x[i].append(x)
                robot_trajectories_y[i].append(y)
                robot_trajectories_theta[i].append(theta)
                robot_trajectories_rgb[0][i].append(r)
                robot_trajectories_rgb[1][i].append(g)
                robot_trajectories_rgb[2][i].append(b)

    robot_trajectories_x_all.append(robot_trajectories_x)
    robot_trajectories_y_all.append(robot_trajectories_y)
    robot_trajectories_theta_all.append(robot_trajectories_theta)
    # store as [r_lists, g_lists, b_lists]
    robot_trajectories_rgb_all.append(robot_trajectories_rgb)
    num_frames_all.append(len(robot_trajectories_x[0]))

# Determine total frames to animate: use max number of frames across simulations

# Auto-detect RGB scale: if maximum RGB value across the loaded data is <= 1.0
# treat values as 0-1 floats; otherwise treat as 0-255 integers. This handles
# datasets where colors are encoded as 1,0,0 or as 255,0,0.
global_max = 0.0
for sim_rgb in robot_trajectories_rgb_all:
    # sim_rgb is [r_lists, g_lists, b_lists]
    for comp in sim_rgb:
        for robot_list in comp:
            if robot_list:
                local_max = max(robot_list)
                if local_max > global_max:
                    global_max = local_max

if rgb_detect:
    if global_max <= 1.01:
        # values already in 0-1
        rgb_0_255 = False
        rgb_divisor = 1.0
        print(f"Detected RGB in 0-1 range (global_max={global_max}). Using rgb_0_255=False")
    else:
        # treat as 0-255
        rgb_0_255 = True
        rgb_divisor = 255.0
        print(f"Detected RGB in 0-255 range (global_max={global_max}). Using rgb_0_255=True")
else:
    # respect the manual rgb_0_255 flag; choose divisor accordingly
    if rgb_0_255:
        rgb_divisor = 255.0
    else:
        rgb_divisor = 1.0
    print(f"Auto-detect disabled: using rgb_0_255={rgb_0_255}, rgb_divisor={rgb_divisor}")
    

total_sim_frames = max(num_frames_all) if num_frames_all else 0
video_frames = total_sim_frames

# Compute a fixed color per robot (use first available RGB sample) so robots
# keep distinct, consistent colors across the whole animation.
robot_fixed_colors_all = []
for sim_rgb in robot_trajectories_rgb_all:
    sim_fixed = []
    r_lists, g_lists, b_lists = sim_rgb
    for i in range(num_robots):
        # find first frame with data for this robot
        r0 = r_lists[i][0] if r_lists[i] else 0.0
        g0 = g_lists[i][0] if g_lists[i] else 0.0
        b0 = b_lists[i][0] if b_lists[i] else 0.0
        # normalize according to divisor (handles 0-1, 0-11, 0-255)
        r_n = float(r0) / rgb_divisor
        g_n = float(g0) / rgb_divisor
        b_n = float(b0) / rgb_divisor
        # clip to [0,1]
        sim_fixed.append((np.clip(r_n, 0.0, 1.0), np.clip(g_n, 0.0, 1.0), np.clip(b_n, 0.0, 1.0)))
    robot_fixed_colors_all.append(sim_fixed)

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
    if sim_idx < len(robot_files):
        for i in range(num_robots):
            # initial circle with fixed robot color (no trajectory line)
            fixed_color = robot_fixed_colors_all[sim_idx][i] if sim_idx < len(robot_fixed_colors_all) else (0.5, 0.5, 0.5)
            circle = Circle((0, 0), diameter_robot / 2.0, facecolor=fixed_color, edgecolor=fixed_color, linewidth=1.0, alpha=0.95)
            ax.add_patch(circle)
            artists['robot_circles'].append(circle)
    plot_artists.append(artists)

def normalize_rgb(r, g, b):
    """Normalize RGB values to [0,1] tuple for matplotlib.
    Accepts either 0-255 integers or 0-1 floats depending on rgb_0_255 flag.
    """
    if rgb_0_255:
        return (np.clip(r, 0, 255) / 255.0, np.clip(g, 0, 255) / 255.0, np.clip(b, 0, 255) / 255.0)
    else:
        return (np.clip(r, 0.0, 1.0), np.clip(g, 0.0, 1.0), np.clip(b, 0.0, 1.0))

def update(frame):
    for sim_idx, ax in enumerate(axes):
        if sim_idx < len(robot_files):
            artists = plot_artists[sim_idx]
            for i in range(num_robots):
                xs = robot_trajectories_x_all[sim_idx][i]
                ys = robot_trajectories_y_all[sim_idx][i]
                thetas = robot_trajectories_theta_all[sim_idx][i]
                rs = robot_trajectories_rgb_all[sim_idx][0][i]
                gs = robot_trajectories_rgb_all[sim_idx][1][i]
                bs = robot_trajectories_rgb_all[sim_idx][2][i]
                idx = min(frame, len(xs) - 1)
                x_last = xs[idx]
                y_last = ys[idx]
                artists['robot_circles'][i].center = (x_last, y_last)
                # use fixed per-robot color (computed from first frame) for consistency
                try:
                    fixed_color = robot_fixed_colors_all[sim_idx][i]
                except Exception:
                    fixed_color = (0.5, 0.5, 0.5)
                # update circle colors (keep fixed)
                artists['robot_circles'][i].set_facecolor(fixed_color)
                artists['robot_circles'][i].set_edgecolor(fixed_color)
                # no trajectory lines to update; only circles are updated
                # No arrow/heading patch: we intentionally omit drawing headings
    return []

ani = FuncAnimation(fig, update, frames=video_frames, blit=False)

output_file = os.path.join(os.path.dirname(__file__), 'sorting_groups_' + generation + '.mp4')
try:
    writer = FFMpegWriter(fps=fps)
    ani.save(output_file, writer=writer, dpi=100)
    print(f"Saved video to {output_file}")
except Exception as e:
    print("Failed to save mp4 via FFMpegWriter. Make sure ffmpeg is installed and available in PATH.")
    print(str(e))
