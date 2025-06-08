import matplotlib.pyplot as plt
import statistics
from pathlib import Path

colors = [
    '#d50000',
    '#e30038',
    '#e9005f',
    '#ec0086',
    '#e800b0',
    '#d436d6',
    '#b359f8',
    '#8375ff',
    '#3e8cff',
    '#009cfa',
    '#00a3e2',
    '#00a8d5',
    '#00adcb',
    '#00b2c0',
    '#00b8b2',
    '#00bf9e',
    '#00c783',
    '#00cc5e',
    '#63cc42',
    '#95c92c'
]

base_dir = Path('/home/anachiarelli/projects/UDESC/tcc/simulation/output/7-6-10bots-20gens-uniform-2')

for generation_dir in base_dir.iterdir():
    if not generation_dir.is_dir():
        continue

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
    plt.title('Geração ' + str(int(generation)))
    plt.plot(average_dispersion_over_time, color = colors[int(generation)])
    plt.grid()
    plt.xlim([0, len(average_dispersion_over_time)])
    plt.ylim([0, 3000]) # TODO
    plt.xlabel('tempo (s/10)')
    plt.ylabel('dispersão')
    #plt.show()
    plt.savefig(generation + '.png')
    plt.clf()
    #break