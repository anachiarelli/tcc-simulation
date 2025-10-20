import matplotlib.pyplot as plt
import statistics
from pathlib import Path
import os

base_dir = Path('/home/anachiarelli/projects/udesc/tcc/simulation/output/grouping/19-10-2025 17-39-39')

for generation_dir in base_dir.iterdir():
    if not generation_dir.is_dir():
        continue

    fitness_by_individual = {}
    with (generation_dir / 'fitness.csv').open() as fitness_file:
        i = 0
        for row in fitness_file:
            individual = str(i).zfill(3)
            fitness_by_individual[individual] = float(row)
            i += 1

    best_individual = None
    for key in fitness_by_individual.keys():
        if (best_individual == None) or (fitness_by_individual[best_individual] < fitness_by_individual[key]):
            best_individual = key

    dispersion_over_time_per_individual = {}
    files = [f for f in sorted(os.listdir(generation_dir / "dispersions")) if f.endswith('_0.csv')]
    for file in files:
        individual = file.split('_')[0]
       
        if individual not in dispersion_over_time_per_individual:
            dispersion_over_time_per_individual[individual] = []

        with (generation_dir / "dispersions" / file).open() as individual_file:
            for row in individual_file:
                dispersion_over_time_per_individual[individual].append(float(row))

    individuals = list(dispersion_over_time_per_individual.keys())
    steps = len(dispersion_over_time_per_individual[individuals[0]])
    
    average_dispersion_over_time = [statistics.mean([dispersion_over_time_per_individual[i][s] for i in individuals]) for s in range(steps)]

    generation = int(generation_dir.name) + 1
    plt.figure(figsize=(6, 4)) 
    #plt.subplots_adjust(top=0.99)
    #plt.title('Dispersão da ' + str(generation) + 'ª geração - 10 robôs')
    plt.plot(dispersion_over_time_per_individual[best_individual], label='Menor dispersão')
    plt.plot(average_dispersion_over_time, linestyle='dotted', label='Média')
    plt.grid()
    plt.xlim([0, len(average_dispersion_over_time)])
    plt.ylim([0, 3000]) # TODO 10 = 3000 100 = 32000
    plt.xlabel('Tempo (s/10)')
    plt.ylabel('Dispersão')
    plt.legend()
    #plt.show()
    plt.savefig(str(generation) + '.png', bbox_inches='tight', pad_inches=0)
    plt.clf()
    plt.close()