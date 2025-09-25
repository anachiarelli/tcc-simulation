import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import os

# Parâmetros
num_robos = 100
diametro_robo = 0.074
diretorio_base = '/home/anachiarelli/projects/udesc/tcc/simulation/output/current'
geracoes_desejadas = ['000', '001', '004', '009', '019', '039']
num_simulacoes = 40
rows, cols = 8, 5
cores = plt.cm.get_cmap('tab10', num_robos)

for geracao in geracoes_desejadas:
    diretorio = os.path.join(diretorio_base, geracao, 'positions')
    arquivos = sorted(os.listdir(diretorio))[:num_simulacoes]

    fig, axes = plt.subplots(rows, cols, figsize=(4, 6.5))  # menos largo

    axes = axes.flatten()

    for sim_count, arquivo in enumerate(arquivos):
        trajetorias_x = [[] for _ in range(num_robos)]
        trajetorias_y = [[] for _ in range(num_robos)]

        with open(os.path.join(diretorio, arquivo), newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                row = [float(value.strip()) for value in row if value.strip()]
                for i in range(num_robos):
                    x = row[2 * i]
                    y = row[2 * i + 1]
                    trajetorias_x[i].append(x)
                    trajetorias_y[i].append(y)

        ax = axes[sim_count]
        ax.set_xlim(0, 316)
        ax.set_ylim(0, 316)
        ax.set_aspect('equal')
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])

        # Título pequeno dentro do plot
        ax.text(0.5, 1.02, f'{sim_count + 1}',
                transform=ax.transAxes, ha='center', va='bottom',
                fontsize=5)

        for i in range(num_robos):
            cor = cores(i)
            ax.plot(trajetorias_x[i], trajetorias_y[i], color=cor, linewidth=0.3)
            ax.plot(trajetorias_x[i][-1], trajetorias_y[i][-1], 'o', color=cor, markersize=2, markeredgecolor='black')
            circulo = Circle((trajetorias_x[i][-1], trajetorias_y[i][-1]), diametro_robo / 2,
                             color=cor, alpha=0.3, edgecolor='black', linewidth=0.3)
            ax.add_patch(circulo)

    for ax in axes[len(arquivos):]:
        ax.axis('off')

    # Ajuste com menos espaço horizontal
    fig.subplots_adjust(
        left=0.03,
        right=0.97,
        top=0.96,
        bottom=0.04,
        wspace=0.05,  # reduzido
        hspace=0.15
    )

    geracao = int(geracao) + 1
    plt.savefig(str(geracao) + '.png', bbox_inches='tight', dpi=100)
    plt.close()
    print(f"Salvo: {geracao}")
