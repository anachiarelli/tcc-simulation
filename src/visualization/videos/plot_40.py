import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import numpy as np
import os
from matplotlib.widgets import Slider


# Parâmetros
num_robos = 10
diametro_robo = 0.074  # metros (7,4 cm)
interpolacoes_por_frame = 1  # mais = mais suave
diretorio = '/home/anachiarelli/projects/udesc/tcc/simulation/output/grouping/02-10-2025 04-28-42/010/positions'  # Diretório com os arquivos de simulação
num_simulacoes = 40  # Número de simulações a exibir
rows, cols = 5, 8  # Layout do grid (5x8 = 40)

# Lista de arquivos no diretório
arquivos = [f for f in os.listdir(diretorio)]
arquivos = arquivos[:num_simulacoes]  # Limita a 40 arquivos

# Inicializa listas para armazenar trajetórias de todas as simulações
trajetorias_x_interp_all = []
trajetorias_y_interp_all = []
num_frames_all = []

# Processa cada arquivo
for arquivo in arquivos:
    trajetorias_x_raw = [[] for _ in range(num_robos)]
    trajetorias_y_raw = [[] for _ in range(num_robos)]

    # Leitura do arquivo
    with open(os.path.join(diretorio, arquivo), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            row = [float(value.strip()) for value in row if value.strip()]
            for i in range(num_robos):
                x = row[3 * i]
                y = row[3 * i + 1]
                trajetorias_x_raw[i].append(x)
                trajetorias_y_raw[i].append(y)

    # Interpolação linear
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

        x_interp.append(x[-1])
        y_interp.append(y[-1])

        trajetorias_x_interp.append(np.array(x_interp))
        trajetorias_y_interp.append(np.array(y_interp))

    trajetorias_x_interp_all.append(trajetorias_x_interp)
    trajetorias_y_interp_all.append(trajetorias_y_interp)
    num_frames_all.append(len(trajetorias_x_interp[0]))

# Determina o número máximo de frames entre todas as simulações
num_frames = max(num_frames_all)

# Setup do grid de subplots para Full HD
fig, axes = plt.subplots(rows, cols, figsize=(18, 8))  # 1920x1080 pixels a 100 DPI
axes = axes.flatten()  # Facilita o acesso aos subplots
cores = plt.cm.get_cmap('tab10', num_robos)

# Inicializa listas para armazenar elementos gráficos
linhas_all = []
marcadores_all = []
circulos_all = []

# Configura cada subplot
for sim_idx, ax in enumerate(axes):
    if sim_idx < len(arquivos):
        ax.set_xlim(0, 316)
        ax.set_ylim(0, 316)
        ax.set_aspect('equal')
        ax.grid(True)
        ax.set_title(f'{sim_idx+1}', fontsize=10)  # Título simplificado e menor
        ax.tick_params(labelsize=5)  # Reduz tamanho das marcas dos eixos

        linhas = []
        marcadores = []
        circulos = []

        for i in range(num_robos):
            cor = cores(i)
            linha, = ax.plot([], [], color=cor, linewidth=0.5)  # Linhas mais finas
            marcador, = ax.plot([], [], 'o', color=cor, markeredgecolor='black', markersize=3)  # Marcadores menores
            circulo = Circle((0, 0), diametro_robo / 2, color=cor, alpha=0.3, edgecolor='black')
            ax.add_patch(circulo)
            linhas.append(linha)
            marcadores.append(marcador)
            circulos.append(circulo)

        linhas_all.append(linhas)
        marcadores_all.append(marcadores)
        circulos_all.append(circulos)
    else:
        ax.axis('off')  # Desativa subplots não utilizados

# Função de atualização para a animação
def update(frame):
    elementos = []
    for sim_idx, ax in enumerate(axes):
        if sim_idx < len(arquivos):
            trajetorias_x = trajetorias_x_interp_all[sim_idx]
            trajetorias_y = trajetorias_y_interp_all[sim_idx]
            num_frames_sim = num_frames_all[sim_idx]
            frame_idx = min(frame, num_frames_sim - 1)  # Evita índices fora do intervalo

            for i in range(num_robos):
                x = trajetorias_x[i]
                y = trajetorias_y[i]
                linhas_all[sim_idx][i].set_data(x[:frame_idx+1], y[:frame_idx+1])
                marcadores_all[sim_idx][i].set_data(x[frame_idx], y[frame_idx])
                circulos_all[sim_idx][i].center = (x[frame_idx], y[frame_idx])
                elementos.extend([linhas_all[sim_idx][i], marcadores_all[sim_idx][i], circulos_all[sim_idx][i]])

    return elementos

# Criação da animação
# ani = FuncAnimation(fig, update, frames=num_frames, interval=1, blit=True)


# Slider para controle de frames
# slider deve estar em um espaço separado
plt.subplots_adjust(bottom=0.2)  # Ajusta o espaço para o slider
axframe = plt.axes([0.25, 0.02, 0.50, 0.02], facecolor='lightgoldenrodyellow')
sframe = Slider(axframe, 'Frame', 0, num_frames - 1, valinit=0, valstep=1)

def update_frame(val):
    frame = int(sframe.val)
    update(frame)
    plt.draw()
sframe.on_changed(update_frame)

# Ajusta o layout para minimizar margens
plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=0.2)  # Reduz espaçamento entre subplots

# print("Salvando vídeo")
# Para salvar (opcional)
# ani.save(f'gen100-40-10.mp4', fps=10, dpi=100)

# Maximiza a janela para Full HD
# plt.get_current_fig_manager().full_screen_toggle()  # Pode variar dependendo do backend

plt.show()