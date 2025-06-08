import matplotlib.pyplot as plt
import statistics
from pathlib import Path

base_dir = Path('/home/anachiarelli/projects/UDESC/tcc/simulation/output/current')

for generation_dir in base_dir.iterdir():
    if not generation_dir.is_dir():
        continue

    fitness_by_individual = {}
    with (generation_dir / 'fitness.txt').open() as fitness_file:
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
    file_names = []
    for file in (generation_dir / "dispersions").iterdir():
        if not file.is_file():
            continue

        individual = file.name[0:3]
       
        if individual not in dispersion_over_time_per_individual:
            dispersion_over_time_per_individual[individual] = []

        with file.open() as individual_file:
            for row in individual_file:
                dispersion_over_time_per_individual[individual].append(float(row))

    individuals = list(dispersion_over_time_per_individual.keys())
    steps = len(dispersion_over_time_per_individual[individuals[0]])
    
    average_dispersion_over_time = [statistics.mean([dispersion_over_time_per_individual[i][s] for i in individuals]) for s in range(steps)]

    generation = generation_dir.name
    plt.figure(figsize=(8, 5)) 
    plt.title('Geração ' + str(int(generation)))
    plt.plot(dispersion_over_time_per_individual[best_individual], label='Menor dispersão', linewidth=3)
    plt.plot(average_dispersion_over_time, linestyle='dotted', label='Média', linewidth=3)
    plt.grid()
    plt.xlim([0, len(average_dispersion_over_time)])
    plt.ylim([0, 3000]) # TODO
    plt.xlabel('Tempo (s/10)')
    plt.ylabel('Dispersão')
    plt.legend()
    #plt.show()
    plt.savefig(generation + '.png')
    plt.clf()
    plt.close()