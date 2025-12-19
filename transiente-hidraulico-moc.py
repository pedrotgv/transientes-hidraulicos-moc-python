import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# --- DADOS SIMULAÇÃO ---
Lt = 1000                # Comprimento da tubulação [m]
Dx = 1                     # Discretização espacial [m]
D = 1                      # Diâmetro Tubulação [m]
f = 0.02                   # Fator de atrito
g = 9.81                   # Gravidade [m/s²]
H0 = 10                    # Nível do reservatório [m]
v0 = round(np.sqrt((H0*2*g)/(1+f*(Lt/D))),2)                     # Velocidade inicial [m/s]
A0 = np.pi * D**2 / 4      # Área da seção Tubulação [m²]
Q0 = v0 * A0               # Vazão inicial [m³/s]
materiais = ['pvc', 'aco', 'concreto']
material=materiais[2]
c = 1000                   # Celeridade Tubulação [m/s]
Dt = Dx / c                # Passo de tempo
TT = 20                    # Tempo total de simulação [s]
Tal = 2 * Lt / c           # Período da tubulação [s]
TF = 0.5*Tal                   # Tempo fechamento Válvula [s]


# --- COEFICIENTES DO MÉTODO DAS CARACTERÍSTICAS ---
Ca = (g * A0) / c
k = f * Dt / (2 * D * A0)


# --- DISCRETIZAÇÃO ---
Nx = int(Lt / Dx)                 # Número de divisões da tubulação
Nt = int(TT / Dt)                 # Número de espaços de tempo
x = np.arange(0, Lt + Dx, Dx)     # Matriz com a distância de cada ponto de divisão da tubulação até o reservatório
tempo = [0]                       # Matriz que vai armazenar os instantes de tempo


# --- MATRIZES DE RESULTADO ---
pressao = np.zeros((Nt+1, Nx+1), dtype=np.float32)          # Cria uma matriz para armazenar os dados de pressão. Cada linha representa as pressões de cada ponto no instante, linha 1 instante t=0, linha 2 instante t=0+1*Dt
vazao = np.zeros((Nt+1, Nx+1), dtype=np.float32)            # Cria uma matriz para armazenar os dados de vazão. Cada linha representa as vazões de cada ponto no instante, linha 1 instante t=0, linha 2 instante t=0+1*Dt
terreno =  np.ones(Nx+1) * 0                                # Cria uma matriz do mesmo tamanho da tubulação que contém o valor da cota topográfica de cada ponto do terreno em que a tubulação esta apoiada.


# --- ESTADO INICIAL --- 
vazao[0, :] = Q0                                            # Define o estado inicial de vazão (t=0s) para vazão constante = Q0

for i in range(Nx+1):                                       # Define o estado inicial de pressão (t=0s) para a pressão em regime permanente H0 - L*J
    perda = f * x[i] * v0**2 / (2 * g * D)
    pressao[0, i] = H0 - perda + (terreno[0]-terreno[i])


# ---  SIMULAÇÃO --- 
for t in range(1, Nt+1):
    # Nesse primeiro loop nos percorremos as matrizes olhando para as suas linhas, que aqui representa um instante de tempo, por isso iniciamos esse loop no indice 1, ignorando a linha zero que contém o estado inicial já calculado
    
    tempo.append(t*Dt)

    for i in range(Nx+1):
        # Nesse segundo loop nos percorremos as linhas e estamos olhando para cada elemento dessa linha, que aqui representa um ponto da tubulação

        if i == 0: # --- RESERVATÓRIO ---
        
            cn = (vazao[t-1, i+1]) - (Ca * pressao[t-1, i+1]) - (k * vazao[t-1, i+1] * abs(vazao[t-1, i+1]))
            
            pressao[t, i] = H0                       # Pressão no reservatório é sempre constante
            vazao[t, i] = cn + Ca * pressao[t, i]    # Vazão é calculada com base nas equações do método das características eq

        elif i == Nx: # --- VÁLVULA ---
            
            vazao_tempo = v0 * (A0-(t*Dt)*(A0/TF))   # Verifica o estádo de fechamento da válvula no tempo em questão

            cp = (vazao[t-1, i-1]) + (Ca * pressao[t-1, i-1]) + (k * vazao[t-1, i-1] * abs(vazao[t-1, i-1]))

            if vazao_tempo >= 0:            # Define a vazão na válvula de acordo com o seu estado de fechamento
                vazao[t, i] = vazao_tempo
            else:
                vazao[t, i] = 0

            pressao[t, i] = (cp - vazao[t, i])/Ca  # Pressão é calculada com base nas equações do método das características eq
            
        else: # --- PONTOS INTERNOS --- 
            
            cn = (vazao[t-1, i+1]) - (Ca * pressao[t-1, i+1]) - (k * vazao[t-1, i+1] * abs(vazao[t-1, i+1]))
            cp = (vazao[t-1, i-1]) + (Ca * pressao[t-1, i-1]) + (k * vazao[t-1, i-1] * abs(vazao[t-1, i-1]))

            pressao[t, i] = (cp - cn) / (2*Ca)    # Pressão é calculada com base nas equações do método das características eq
            vazao[t, i] = (cp + cn) / 2           # Vazão é calculada com base nas equações do método das características eq


# --- SELECIONA DADOS DE INTERESSE ---
envol_max = np.max(pressao, axis=0)     # Olha a matriz de pressões e seleciona o maior valor de cada ponto.
envol_min = np.min(pressao, axis=0)     # Olha a matriz de pressões e seleciona o menor valor de cada ponto.
coluna_v_final = vazao[:, Nx]           # Olha a matriz de vazões e seleciona a última coluna.

# --- CRIAÇÃO DA ANIMAÇÃO ---
## --- Gráfico da pressão ao longo da tubulação que será utilizado na animação ---
fig1, ax1 = plt.subplots(figsize=(7,5))

ax1.set_ylim(min(np.min(pressao), np.min(terreno))-10, np.max(pressao)+terreno[0])

linha_pressao, = ax1.plot(x, pressao[0]+terreno, color='red', label='Pressão')
linha_terreno, = ax1.plot(x, terreno, color='k', label='Tubulação', linestyle='--', alpha=0.8)
texto_tempo = ax1.text(0.02, 0.95, '', transform=ax1.transAxes)

ax1.set_xlabel("Comprimento (m)")
ax1.set_ylabel("Carga (m.c.a)")
ax1.set_title("Pressão no tempo")
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7 )


# --- CRIAÇÃO DOS GRÁFICOS ---
fig2, ax2 = plt.subplots(2, 1, figsize=(15, 20))
fig2.suptitle("Caso 2", fontsize=18, y=0.98)

texto = f"Dx={Dx} m, Lx={Lt} m, D={D} m, f={f}, c={c} m/s, Material: {material} TF={round(TF/Tal,2)}τ s, H0={H0} m.c.a, V0={v0} m/s"
fig2.text(0.5, 0.02, texto, ha='center', va='bottom', fontsize=12)


## --- Gráfico das envoltórias ---
envolt_max = ax2[0].plot(x, envol_max+terreno, color="r", label='Pressão máxima')
envolt_min = ax2[0].plot(x, envol_min+terreno, color="b", label='Pressão mínima')
ax2[0].fill_between(x, envol_min + terreno, envol_max + terreno, color='lightgray', alpha=0.6, label='Envoltória')
linha_terreno, = ax2[0].plot(x, terreno, color='k', label='Tubulação', linestyle='--', alpha=0.8)
ax2[0].set_xlabel("Comprimento (m)")
ax2[0].set_ylabel("Pressão (m.c.a)")
ax2[0].set_title("Envoltória de pressões")
ax2[0].legend(loc='upper left', fontsize=10)
ax2[0].grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7 )
ax2[0].text(Lt-200,terreno[0]-20, f'Máximo = {np.max(pressao):.2f}\nMínimo = {np.min(pressao):.2f}', fontsize=10)

## --- Gráfico da vazão na válvula ---
vazao_valv, = ax2[1].plot(tempo, coluna_v_final, color='b', label='Vazão')
ax2[1].set_xlabel("Tempo (s)")
ax2[1].set_ylabel("Vazão (m³/s)")
ax2[1].set_title("Vazão na válvula")
ax2[1].legend(loc='upper left', fontsize=10)
ax2[1].grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7 )

## --- Função para atualizar o gráfico da pressão no tempo ---
def atualizar_p(frame):
    linha_pressao.set_ydata(pressao[frame]+terreno)
    texto_tempo.set_text(f'Tempo: {frame*Dt:.2f} s')
    return linha_pressao, texto_tempo

anim_p = FuncAnimation(fig1, atualizar_p, frames=Nt, interval=1, blit=True)

plt.show()