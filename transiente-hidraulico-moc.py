import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
from tqdm import tqdm
import time


pasta_saida = "graficos"    # Cria o nome da pasta para salvar gráficos e animações
os.makedirs(pasta_saida, exist_ok=True)      # Cria a pasta para salvar gráficos e animações
animacao = False     # Define se vai ser gerada a animação

# --- CASOS SIMULADOS ---
casos = [[1, 1,1118.8, 0.5, 20],
         [1, 0.1,1118.8, 0.5, 20],
         [1, 0.5,1118.8, 0.5, 20],
         [10, 1,1118.8, 0.5, 20],
         [0.1, 1,1118.8, 0.5, 2],
         [1, 1,1118.8, 0.1, 20],
         [1, 1,1118.8, 2, 20],
         [1, 1,294.7, 0.5, 20],
         [1, 1,530.5, 0.5, 20],
]
# Essa é a matriz com os dados de todos os casos simulados, na ordem: Dx, D, Material (c) , Tal, Tempo de simulação

celeridades = {'pvc':294.7, 'aco':1118.8, 'concreto':530.5 } # Materiais e respectivas celeridades (pvc, aco e concreto)

tempo_casos = []    # Matriz para simular o tempo dos casos
tabela_maximos = []

for caso_simulado in tqdm(range(len(casos)), desc="Simulando casos"):
    t_inicio = time.time()

    # --- DADOS SIMULAÇÃO ---
    Lt = 1000                  # Comprimento da tubulação [m]
    f = 0.02                   # Fator de atrito
    g = 9.81                   # Gravidade [m/s²]
    H0 = 10                    # Nível do reservatório [m]

    Dx = casos[caso_simulado][0]                    # Discretização espacial [m]
    D = casos[caso_simulado][1]                     # Diâmetro Tubulação [m]
    c = casos[caso_simulado][2]                       # Celeridade Tubulação [m/s]
    TT = casos[caso_simulado][4]                    # Tempo total de simulação [s]

    v0 = round(np.sqrt((H0*2*g)/(1+f*(Lt/D))),2)    # Velocidade inicial [m/s]
    A0 = np.pi * D**2 / 4                           # Área da seção Tubulação [m²]
    Q0 = v0 * A0                                    # Vazão inicial [m³/s]

    Dt = Dx / c                                     # Passo de tempo                  
    Tal = 2 * Lt / c                                # Período da tubulação [s]
    TF = casos[caso_simulado][3]*Tal                # Tempo fechamento Válvula [s]


    # --- COEFICIENTES DO MÉTODO DAS CARACTERÍSTICAS ---
    Ca = (g * A0) / c
    k = f * Dt / (2 * D * A0)


    # --- DISCRETIZAÇÃO ---
    Nx = int(Lt / Dx)                 # Número de divisões da tubulação
    Nt = int(TT / Dt)                 # Número de espaços de tempo
    x = np.arange(0, Lt + Dx, Dx)     # Matriz com a distância de cada ponto de divisão da tubulação até o reservatório
    tempo = [0]                       # Matriz que vai armazenar os instantes de tempo


    # --- MATRIZES DE RESULTADO ---
    pressao = np.zeros((Nt+1, Nx+1), dtype=np.float32)          # Matriz para armazenar os dados de pressão.
    vazao = np.zeros((Nt+1, Nx+1), dtype=np.float32)            # Matriz para armazenar os dados de vazão.
    terreno =  np.ones(Nx+1) * 1000                             # Matriz que contém o valor da cota topográfica da tubulação.


    # --- ESTADO INICIAL --- 
    vazao[0, :] = Q0               # Define o estado inicial de vazão (t=0s) para vazão constante = Q0

    for i in range(Nx+1):          # Define o estado inicial de pressão (t=0s) para a pressão em regime permanente H0 - L*J
        perda = f * x[i] * v0**2 / (2 * g * D)
        pressao[0, i] = H0 - perda + (terreno[0]-terreno[i])


    # ---  SIMULAÇÃO --- 
    for t in tqdm(range(1, Nt+1), desc=f"Caso {caso_simulado} – tempo", leave=False):
                
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

    tabela_maximos.append([caso_simulado, np.max(pressao),np.min(pressao)])

    # --- CRIAÇÃO DA ANIMAÇÃO ---
    ## --- Gráfico da pressão ao longo da tubulação que será utilizado na animação ---
    if animacao:
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
    fig2.suptitle(f"Caso {caso_simulado}", fontsize=18, y=0.98)

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
    if animacao:
        def atualizar_p(frame):
            linha_pressao.set_ydata(pressao[frame]+terreno)
            texto_tempo.set_text(f'Tempo: {frame*Dt:.2f} s')
            return linha_pressao, texto_tempo

        anim_p = FuncAnimation(fig1, atualizar_p, frames=Nt, interval=1, blit=True)

    if animacao:
        nome_anim = f"animacao_caso_{caso_simulado}.gif"
        caminho_anim = os.path.join(pasta_saida, nome_anim)
        anim_p.save(caminho_anim, writer="pillow", fps=30)
        plt.close(fig1)

    nome_arquivo = f"caso_{caso_simulado}.png"  # Define o nome do arquivo para salvar o gráfico
    caminho = os.path.join(pasta_saida, nome_arquivo)     # Define o caminho para salvar a imagem

    plt.savefig(caminho, dpi=300, bbox_inches="tight")    # 
    plt.close(fig2)   # MUITO IMPORTANTE, FECHA A IMAGEM PARA SIMULAR O PRXIMO CASO COM UM GRÁFICO VAZIO.

    t_fim = time.time()
    tempo_caso = t_fim - t_inicio
    tempo_casos.append(tempo_caso)

print("\nResumo dos tempos de simulação:")

for i, tempo in enumerate(tempo_casos):
    print(f"Caso {i}: {tempo:.2f} s")

print(f"\nTempo total: {sum(tempo_casos):.2f} s")
print(f"Tempo médio por caso: {np.mean(tempo_casos):.2f} s")

caminho_tempo = os.path.join(pasta_saida, "resumo_tempos_simulacao.txt")

with open(caminho_tempo, "w", encoding="utf-8") as f:
    f.write("Resumo dos tempos de simulação:\n\n")

    for i, tempo in enumerate(tempo_casos):
        f.write(f"Caso {i}: {tempo:.2f} s\n")

    f.write(f"\nTempo total: {sum(tempo_casos):.2f} s\n")
    f.write(f"Tempo médio por caso: {np.mean(tempo_casos):.2f} s\n")

tabela_maximos = np.array(tabela_maximos)
caminho_tabela = os.path.join(pasta_saida, "resumo_pressao.csv")
np.savetxt(
    caminho_tabela,
    tabela_maximos,
    delimiter=";",
    header="caso,pressao_maxima,pressao_minima",
    comments="",
    fmt=["%d", "%.6f", "%.6f"]
)
