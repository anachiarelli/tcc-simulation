import matplotlib.pyplot as plt
import statistics
from pathlib import Path
import numpy as np

base_dir = Path('/home/anachiarelli/projects/udesc/tcc/simulation/output/current')

fitnesses_by_generation = []

generations = []
for generation_dir in base_dir.iterdir():
    if not generation_dir.is_dir():
        continue
    generations.append(generation_dir.name)
generations.sort()

for generation in generations:
    fitnesses = []
    with (base_dir / generation / 'fitness.txt').open() as fitness_file:
        for row in fitness_file:
            fitnesses.append(float(row))
    fitnesses.sort()
    fitnesses_by_generation.append(fitnesses)

average_fitness_by_generation = [statistics.mean(fitnesses) for fitnesses in fitnesses_by_generation]
maximum_fitness_by_generation = [max(fitnesses) for fitnesses in fitnesses_by_generation]

# Grouped bar chart setup
plt.figure(figsize=(10, 6))  # Adjust figure size for better visibility
bar_width = 0.35  # Width of each bar
index = np.arange(len(generations))  # X-axis indices for generations

# Plot bars for maximum and average fitness side by side
plt.bar(index, maximum_fitness_by_generation, bar_width, label='Melhor fitness')
plt.bar(index + bar_width, average_fitness_by_generation, bar_width, label='Média')

# Customize the plot
plt.title('Fitness por Geração')
plt.xlabel('Geração')
plt.ylabel('Fitness')
plt.xticks(index + bar_width / 2, [int(generation) + 1 for generation in generations])  # Center x-ticks under grouped bars
plt.legend()
plt.grid(True, axis='y')  # Grid only on y-axis for clarity
plt.xlim([-0.5, len(generations)])  # Adjust x-axis limits
# plt.ylim([0, 3000])  # Uncomment if you want to set a specific y-axis limit
plt.tight_layout()  # Adjust layout to prevent label cutoff

# Save and clear the plot
plt.savefig('fitness_by_generation.png')
plt.clf()