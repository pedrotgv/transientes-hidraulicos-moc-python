import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
from tqdm import tqdm
import time


pasta_saida = "graficos_slicing"    # Cria o nome da pasta para salvar gráficos e animações
os.makedirs(pasta_saida, exist_ok=True)      # Cria a pasta para salvar gráficos e animações
animacao = False     # Define se vai ser gerada a animação


# Define os casos simulados, na ordem: [0]Dx (m), [1]Di (mm), [2]e(mm), [3]kt, [4]TF(s), [5]TT(s), [6]Material
casos = [ [1, 105.3, 4.5, 0.5, 0.5, 60, 'Aço'],
         [1, 155.1, 5 , 0.5, 0.5, 60,'Aço'],
         [1, 52.8, 3.75, 0.5, 0.5, 60,'Aço'],
         [0.1, 105.3, 4.5, 0.5, 0.5, 20, 'Aço'],
         [10, 105.3, 4.5, 0.5, 0.5, 60, 'Aço'],
         [1, 105.3, 4.5, 0.5, 0.1, 60, 'Aço'],
         [1, 105.3, 4.5, 0.5, 2, 60, 'Aço'],
         [1, 94.4, 7.8, 18, 0.5, 60,'PVC'],
         [1, 72.8, 6.1, 18, 0.5, 60,'PVC'],
         [1, 51.4, 4.3, 18, 0.5, 60,'PVC'],
]

tempo_casos = []    # Matriz para simular o tempo dos casos
tabela_maximos = []     # Cria uma tabela para armazenar os valores de máximos e mínimos de cada simulação
cota_terreno = 0     # Define uma cota para a tubulação horizontal


for caso_simulado in tqdm(range(len(casos)), desc="Simulando casos"):     # Inicia a simulação de cada caso, gerenciando o tempo de simulação

    t_inicio = time.time()    # Inicia o monitoramento de tempo da simulação total

    # --- DADOS SIMULAÇÃO ---
    Lt = 1000                  # Comprimento da tubulação [m]
    f = 0.02                   # Fator de atrito
    g = 9.81                   # Gravidade [m/s²]
    H0 = 10                    # Nível do reservatório [m]

    Dx = casos[caso_simulado][0]                    # Discretização espacial [m]
    D = round(casos[caso_simulado][1]/1000,2)                     # Diâmetro Tubulação [m]

    c = 9900/np.sqrt(48.3+(casos[caso_simulado][3]*(casos[caso_simulado][1]/casos[caso_simulado][2])))  # Celeridade Tubulação [m/s]

    TT = casos[caso_simulado][5]                    # Tempo total de simulação [s]
    material = casos[caso_simulado][6]

    v0 = round(np.sqrt((H0*2*g)/(1+f*(Lt/D))),2)    # Velocidade inicial [m/s]
    A0 = np.pi * D**2 / 4                           # Área da seção Tubulação [m²]
    Q0 = v0 * A0                                    # Vazão inicial [m³/s]

    Dt = Dx / c                                     # Passo de tempo                  
    Tal = 2 * Lt / c                                # Período da tubulação [s]
    TF = casos[caso_simulado][4]*Tal                # Tempo fechamento Válvula [s] (Uma fração do período)


    # --- COEFICIENTES DO MÉTODO DAS CARACTERÍSTICAS ---
    Ca = round((g * A0) / c,6)
    k = round(f * Dt / (2 * D * A0),6)


    # --- DISCRETIZAÇÃO ---
    Nx = int(Lt / Dx)                 # Número de divisões da tubulação
    Nt = int(TT / Dt)                 # Número de espaços de tempo
    x = np.arange(0, Lt + Dx, Dx)     # Matriz com a distância de cada ponto de divisão da tubulação até o reservatório
    tempo = [0]                       # Matriz que vai armazenar os instantes de tempo


    # --- MATRIZES DE RESULTADO ---
    pressao = np.zeros((Nt+1, Nx+1), dtype=np.float32)          # Matriz para armazenar os dados de pressão.
    vazao = np.zeros((Nt+1, Nx+1), dtype=np.float32)            # Matriz para armazenar os dados de vazão.
    terreno =  np.ones(Nx+1) * cota_terreno                     # Matriz que contém o valor da cota topográfica da tubulação.


    # --- ESTADO INICIAL --- 
    vazao[0, :] = Q0               # Define o estado inicial de vazão (t=0s) para vazão constante = Q0

    for i in range(Nx+1):          # Define o estado inicial de pressão (t=0s) para a pressão em regime permanente H0 - L*J
        perda = f * x[i] * v0**2 / (2 * g * D)
        pressao[0, i] = H0 - perda + (terreno[0]-terreno[i])

                
        # ---  SIMULAÇÃO (Vetorizada) --- 
    for t in tqdm(range(1, Nt+1), desc=f"Caso {caso_simulado} – tempo", leave=False):     # Inicia a simulaçao olhando para cada tempo
                
        tempo.append(t*Dt)     # Insere o valor do tempo em uma tabela para gerar os gráficos      

        # ---------------------------------------------------------
        # 1. PONTOS INTERNOS (Cálculo simultâneo de i=1 até Nx-1)
        # ---------------------------------------------------------
        
        # Fatiamento dos vizinhos anteriores
        Q_esq = vazao[t-1, 0:-2]  # Vizinho i-1 (Q_A)
        P_esq = pressao[t-1, 0:-2]
        
        Q_dir = vazao[t-1, 2:]    # Vizinho i+1 (Q_B)
        P_dir = pressao[t-1, 2:]
        
        # --- Método das Características com Linearização do Atrito
        Cp = Q_esq + Ca * P_esq
        Cn = Q_dir - Ca * P_dir
        
        fator_atrito =  k * (np.abs(Q_esq) + np.abs(Q_dir))
        
        # Cálculo final da Vazão (Qp) com o denominador
        vazao[t, 1:-1] = (Cp + Cn) / (2 + fator_atrito)
        
        # Cálculo da Pressão (Hp)
        pressao[t, 1:-1] = (Cp - Cn) / (2 * Ca) 

        # ---------------------------------------------------------
        # 2. CONDIÇÕES DE CONTORNO (Reservatório e Válvula)
        # ---------------------------------------------------------

        # --- RESERVATÓRIO (i = 0) ---
        # Usa o vizinho i+1 (índice 1) do tempo anterior
        cn_res = vazao[t-1, 1] - Ca * pressao[t-1, 1] - k * vazao[t-1, 1] * abs(vazao[t-1, 1])
        
        pressao[t, 0] = H0
        vazao[t, 0] = cn_res + Ca * pressao[t, 0]

        # --- VÁLVULA (i = Nx, ou índice -1) ---
        # Usa o vizinho i-1 (índice -2) do tempo anterior
        Cp_valv = vazao[t-1, -2] + Ca * pressao[t-1, -2] + k * vazao[t-1, -2] * abs(vazao[t-1, -2])

        vazao_tempo = v0 * (A0 - (t*Dt)*(A0/TF))   # Verifica o estado de fechamento

        if vazao_tempo >= 0:
            vazao[t, -1] = vazao_tempo
        else:
            vazao[t, -1] = 0

        pressao[t, -1] = (Cp_valv - vazao[t, -1]) / Ca

    # --- SELECIONA DADOS DE INTERESSE ---
    envol_max = np.max(pressao, axis=0)                    # Olha a matriz de pressões e seleciona o maior valor de cada ponto.
    envol_min = np.min(pressao, axis=0)                    # Olha a matriz de pressões e seleciona o menor valor de cada ponto.
    coluna_v_final = vazao[:, Nx]                          # Olha a matriz de vazões e seleciona a última coluna.
    coluna_m_pressao = pressao[:, pressao.shape[1] // 2]   # Olha a matriz de pressão e seleciona a coluna do meio

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
    fig2.suptitle(f"Caso {caso_simulado}", fontsize=18, y=0.92)

    texto = f"Dx={Dx} m, Lx={Lt} m, Di={D} m, f={f}, c={round(c,2)} m/s, Material: {material} TF={round(TF/Tal,2)}τ ({round(TF,2)}s), H0={H0} m.c.a, V0={v0} m/s, M({Nt}x{Nx})"
    fig2.text(0.5, 0.02, texto, ha='center', va='bottom', fontsize=12)

    ## --- Gráfico das envoltórias ---
    envolt_max = ax2[0].plot(x, envol_max+terreno, color="r", label='Pressão máxima')
    envolt_min = ax2[0].plot(x, envol_min+terreno, color="b", label='Pressão mínima')
    ax2[0].fill_between(x, envol_min + terreno, envol_max + terreno, color='lightgray', alpha=0.6, label='Envoltória')
    linha_terreno, = ax2[0].plot(x, terreno, color='k', label='Tubulação', linestyle='--', alpha=0.8)
    ax2[0].set_xlabel("Comprimento (m)")
    ax2[0].set_ylabel("Pressão (m.c.a)")
    ax2[0].set_title("Envoltória de pressões (a)")
    ax2[0].legend(loc='upper left', fontsize=10)
    ax2[0].grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7 )
    
    ax2[0].text(0.02, 0.1, f'Máximo = {np.max(pressao):.2f}\nMínimo = {np.min(pressao):.2f}', 
                transform=ax2[0].transAxes, fontsize=10, verticalalignment='top', 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
                )
    """
    ## --- Gráfico da vazão na válvula ---
    vazao_valv, = ax2[1].plot(tempo, coluna_v_final, color='b', label='Vazão')
    ax2[1].set_xlabel("Tempo (s)")
    ax2[1].set_ylabel("Vazão (m³/s)")
    ax2[1].set_title("Vazão na válvula")
    ax2[1].legend(loc='upper left', fontsize=10)
    ax2[1].grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7 )
    """

    ## --- Gráfico da pressão no meio da tubulação ---
    pressao_meio, = ax2[1].plot(tempo, coluna_m_pressao, color='b', label='Pressão')
    ax2[1].set_xlabel("Tempo (s)")
    ax2[1].set_ylabel("Pressão (m.c.a.)")
    ax2[1].set_title("Pressão no meio (b)")
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
