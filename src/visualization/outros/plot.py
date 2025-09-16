import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import numpy as np

# Parâmetros
num_robos = 100
diametro_robo = 0.074  # metros (7,4 cm)
interpolacoes_por_frame = 1  # mais = mais suave

# Inicializa as trajetórias
trajetorias_x_raw = [[] for _ in range(num_robos)]
trajetorias_y_raw = [[] for _ in range(num_robos)]

# Leitura do arquivo
with open('../../output/100 robots/012_00101010000010011111101101100111.txt', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        row = [float(value.strip()) for value in row if value.strip()]
        for i in range(num_robos):
            x = row[2 * i]
            y = row[2 * i + 1]
            trajetorias_x_raw[i].append(x)
            trajetorias_y_raw[i].append(y)

# Interpolação linear entre os pontos
trajetorias_x_interp = []
trajetorias_y_interp = []

for i in range(num_robos):
    x = np.array(trajetorias_x_raw[i])
    y = np.array(trajetorias_y_raw[i])

    x_interp = []
    y_interp = []
    
    for j in range(len(x) - 1):
        x_steps = np.linspace(x[j], x[j+1], interpolacoes_por_frame, endpoint=False)
        y_steps = np.linspace(y[j], y[j+1], interpolacoes_por_frame, endpoint=False)
        x_interp.extend(x_steps)
        y_interp.extend(y_steps)

    # Adiciona o último ponto
    x_interp.append(x[-1])
    y_interp.append(y[-1])

    trajetorias_x_interp.append(np.array(x_interp))
    trajetorias_y_interp.append(np.array(y_interp))

# Determina o número total de frames interpolados
num_frames = len(trajetorias_x_interp[0])

# Setup do gráfico
fig, ax = plt.subplots(figsize=(10, 8))
cores = plt.cm.get_cmap('tab10', num_robos)
linhas = []
marcadores = []
circulos = []

for i in range(num_robos):
    cor = cores(i)
    linha, = ax.plot([], [], color=cor)
    marcador, = ax.plot([], [], 'o', color=cor, markeredgecolor='black')
    circulo = Circle((0, 0), diametro_robo / 2, color=cor, alpha=0.3, edgecolor='black')
    ax.add_patch(circulo)
    linhas.append(linha)
    marcadores.append(marcador)
    circulos.append(circulo)

# Ajuste de limites (fixar arena em 316x316 metros)
ax.set_xlim(0, 316)  # -158 a 158
ax.set_ylim(0, 316)

ax.set_title('Animação Suave das Trajetórias dos Robôs')
ax.set_aspect('equal')
ax.grid(True)
ax.legend()

# Função de atualização
def update(frame):
    for i in range(num_robos):
        x = trajetorias_x_interp[i]
        y = trajetorias_y_interp[i]
        linhas[i].set_data(x[:frame+1], y[:frame+1])
        marcadores[i].set_data(x[frame], y[frame])
        circulos[i].center = (x[frame], y[frame])
    return linhas + marcadores + circulos

# Criação da animação com passos interpolados
ani = FuncAnimation(fig, update, frames=num_frames, interval=1, blit=True)

# Para salvar (opcional)
#ani.save('sim.mp4', fps=20, dpi=200)

plt.show()