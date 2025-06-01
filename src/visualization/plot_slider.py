import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import numpy as np

# Parâmetros
num_robos = 100
diametro_robo = 0.074  # metros (7,4 cm)
interpolacoes_por_frame = 10  # mais = mais suave

# Inicializa as trajetórias
trajetorias_x_raw = [[] for _ in range(num_robos)]
trajetorias_y_raw = [[] for _ in range(num_robos)]

# Leitura do arquivo
with open('../../output/001_11111000000101010000010110000000.txt', newline='') as csvfile:
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
plt.subplots_adjust(bottom=0.15)  # espaço para o slider embaixo
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
ax.set_xlim(0, 316)
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
    fig.canvas.draw_idle()
    return linhas + marcadores + circulos

# Inicializa com frame 0
update(0)

# Slider
ax_slider = plt.axes([0.15, 0.05, 0.7, 0.03])  # posição do slider: esquerda, baixo, largura, altura
slider = Slider(ax_slider, 'Frame', 0, num_frames-1, valinit=0, valfmt='%0.0f')

def slider_update(val):
    frame = int(slider.val)
    update(frame)

slider.on_changed(slider_update)

plt.show()
