import numpy as np
import matplotlib.pyplot as plt
import os
import h5py as h5
from casos import casos

pasta_saida = "resultados_graficos_h5"    # Define a pasta onde os gráficos serão salvos
os.makedirs(pasta_saida, exist_ok=True)  

with h5.File('dados_simulacao.h5', 'r') as hdf:
    for caso_simulado in range(len(casos)):
        nome_caso = f'caso_{caso_simulado}'
        grupo_atual = hdf[nome_caso]

        Dx = grupo_atual.attrs['Dx']
        D = grupo_atual.attrs['Di']
        e = grupo_atual.attrs['e']
        kt = grupo_atual.attrs['kt']
        TF = grupo_atual.attrs['TF']
        TT = grupo_atual.attrs['TT']
        material = casos[caso_simulado][6]
        Lt = grupo_atual.attrs['Lt']
        pressao = grupo_atual['pressao'][:]
        vazao = grupo_atual['vazao'][:]
        tempo = grupo_atual['tempo'][:]
        x = grupo_atual['posicao_x'][:]
        terreno = grupo_atual['terreno'][:]
        envol_max = np.max(pressao, axis=0)
        envol_min = np.min(pressao, axis=0)
        coluna_m_pressao = pressao[:, len(x)//2]
        tabela_maximos=grupo_atual['tabela_maximos'][:]
   
        # --- GRÁFICOS ---
        fig, ax = plt.subplots(1,2, figsize=(50, 25))


        ## --- Gráfico das envoltórias ---

        envolt_max = ax[0].plot(x, envol_max+terreno, color="r", label='Pressão máxima')

        envolt_min = ax[0].plot(x, envol_min+terreno, color="b", label='Pressão mínima')

        ax[0].fill_between(x, envol_min + terreno, envol_max + terreno, color='lightgray', alpha=0.6, label='Envoltória')

        linha_terreno, = ax[0].plot(x, terreno, color='k', label='Tubulação', linestyle='--', alpha=0.8)

        ax[0].set_xlabel("Comprimento (m)", fontsize=30)
        ax[0].set_ylabel("Pressão (m.c.a)", fontsize=30)
        ax[0].set_xlim(0, Lt)
        ax[0].set_ylim(-140, 170)

        #ax[0].set_aspect('equal') # Se quiser que o gráfico possua a mesma escala no eixo x e y

        ax[0].tick_params(axis='both', labelsize=25)
        ax[0].grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7 )

        ax[0].text(0.02, 0.2, f'Máximo = {np.max(pressao):.2f}\nMínimo = {np.min(pressao):.2f}', 
                    transform=ax[0].transAxes, fontsize=25, verticalalignment='top', 
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
                    )

        ## --- Gráfico da pressão no meio da tubulação ---

        pressao_meio, = ax[1].plot(tempo, coluna_m_pressao, color='b', label='Pressão')

        ax[1].set_xlabel("Tempo (s)",fontsize=30)
        ax[1].set_ylabel("Pressão (m.c.a.)", fontsize=30)
        ax[1].set_xlim(0, 60)
        ax[1].set_ylim(-140, 170)

        #ax[1].set_aspect('equal') # Se quiser que o gráfico possua a mesma escala no eixo x e y

        ax[1].tick_params(axis='both', labelsize=25)
        ax[1].grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7 )

        caminho = os.path.join(pasta_saida, f"caso_{caso_simulado}.png")    # Salva o primeiro gráfico
        fig.savefig(caminho, dpi=300, bbox_inches="tight")
        plt.close(fig)

        tabela_maximos = np.array(tabela_maximos)    # Salva os dados das pressões máximas e mínimas em uma tabela.
        caminho_tabela = os.path.join(pasta_saida, "resumo_pressao.csv")

        np.savetxt(
        caminho_tabela,
        tabela_maximos,
        delimiter=";",
        header="caso,pressao_maxima,pressao_minima",
        comments="",
        fmt=["%d", "%.6f", "%.6f"]
        )