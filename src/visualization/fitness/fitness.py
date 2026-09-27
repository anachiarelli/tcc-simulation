import matplotlib.pyplot as plt
import statistics
from pathlib import Path
import numpy as np

#base_dir = Path('/home/anachiarelli/projects/udesc/tcc/simulation/output/grouping/20-10-2025 15-47-53') # article aggregation
#base_dir = Path('/home/anachiarelli/projects/udesc/tcc/simulation/output/object_clustering/06-11-2025 01-59-33/') # article object clustering
base_dir = Path('/home/anachiarelli/projects/udesc/tcc/simulation/output/sorting_groups/31-10-2025 02-14-17/') # article multitask aggregation

fitnesses_by_generation = []

generations = []
for generation_dir in base_dir.iterdir():
    if not generation_dir.is_dir():
        continue
    generations.append(generation_dir.name)
generations.sort()

for generation in generations:
    fitnesses = []
    if not (base_dir / generation / 'fitness.csv').is_file():
        generations = generations[:generations.index(generation)]
        break
    with (base_dir / generation / 'fitness.csv').open() as fitness_file:
        for row in fitness_file:
            fitnesses.append(float(row) * 100)
    fitnesses.sort()
    fitnesses_by_generation.append(fitnesses)

average_fitness_by_generation = [statistics.mean(fitnesses) for fitnesses in fitnesses_by_generation]
maximum_fitness_by_generation = [max(fitnesses) for fitnesses in fitnesses_by_generation]

# Line chart setup
plt.figure(figsize=(10, 6))  # Adjust figure size for better visibility
index = np.arange(len(generations))  # X-axis indices for generations

# Plot lines for maximum and average fitness
plt.plot(index, maximum_fitness_by_generation, marker='o', markersize=4, linestyle='-', linewidth=0.8, label='Melhor fitness')
plt.plot(index, average_fitness_by_generation, marker='s', markersize=4, linestyle='--', linewidth=0.8, label='Média')
#plt.plot(index, maximum_fitness_by_generation, marker='o', markersize=4, linestyle='-', linewidth=0.8, label='Best Individual')
#plt.plot(index, average_fitness_by_generation, marker='s', markersize=4, linestyle='--', linewidth=0.8, label='Average Fitness')

# Customize the plot
# plt.title('Fitness por Geração')
# plt.xlabel('Geração')
# plt.ylabel('Fitness')
plt.title('Fitness por Geração')
#plt.title('Fitness by Generation')
plt.xlabel('Geração')
#plt.xlabel('Generation')
plt.ylabel('Fitness')
try:
    xtick_labels_all = [int(generation) for generation in generations]
except Exception:
    xtick_labels_all = generations

# Choose tick positions every 10 generations (0-based index). Always include the last generation.
if len(generations) == 0:
    tick_positions = []
else:
    tick_positions = list(range(0, len(generations), 10))
    if (len(generations) - 1) not in tick_positions:
        tick_positions.append(len(generations) - 1)

tick_labels = [xtick_labels_all[i] for i in tick_positions]
plt.xticks(tick_positions, tick_labels)
plt.legend()
plt.grid(True, axis='y')  # Grid only on y-axis for clarity
plt.xlim([-0.5, max(len(generations) - 0.5, 0)])  # Adjust x-axis limits
# plt.ylim([0, 3000])  # Uncomment if you want to set a specific y-axis limit
plt.tight_layout()  # Adjust layout to prevent label cutoff

# Save and clear the plot
plt.savefig('multitask_fitness.png')
plt.clf()