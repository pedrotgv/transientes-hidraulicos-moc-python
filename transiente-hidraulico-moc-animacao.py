import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import h5py as h5
from casos import casos  # Certifique-se que o arquivo casos.py está na mesma pasta

pasta_saida = "animacao"                     # Cria o nome da pasta para salvar gráficos e animações
os.makedirs(pasta_saida, exist_ok=True)      # Cria a pasta para salvar gráficos e animações
animacao = True                              # Define se vai ser gerada a animação
caso_simulado = 0
resolucao = 1000
fonte = 22
fonte_1 = 17

with h5.File('dados_simulacao.h5', 'r') as hdf:
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
    tabela_maximos = grupo_atual['tabela_maximos'][:]

    # --- DEFINIÇÃO DAS VARIÁVEIS DE TEMPO ---
    Nt = pressao.shape[0]  # Total de passos de tempo guardados na matriz
    Dt = tempo[1] - tempo[0] if len(tempo) > 1 else 0.01  # Calcula o delta t original

    # --- GRÁFICOS ---
    # --- CRIAÇÃO DA ANIMAÇÃO ---
    if animacao:
        # Ajustado o tamanho da figura
        fig1, ax1 = plt.subplots(figsize=(12, 8))

        # Define os limites dos eixos baseado no mínimo e máximo global medido
        ax1.set_xlim(0, Lt)
        ax1.set_ylim(np.min(pressao + terreno) - 10, np.max(pressao + terreno) + 10)

        linha_pressao, = ax1.plot(x, pressao[0] + terreno, color='red', label='Pressão', linewidth=2)
        linha_terreno, = ax1.plot(x, terreno, color='k', label='Tubulação', linestyle='--', alpha=0.8)
        texto_tempo = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, fontsize=fonte_1, fontweight='bold')

        ax1.set_xlabel("Comprimento (m)", fontsize=fonte)
        ax1.set_ylabel("Carga (m.c.a)", fontsize=fonte)
        ax1.set_title(f"Pressão no Tempo - Caso {caso_simulado} ({material})", fontsize=fonte)
        ax1.legend(loc='upper right', fontsize=fonte_1)
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)

        ## --- Função para atualizar o gráfico da pressão no tempo ---
        def atualizar_p(frame):
            linha_pressao.set_ydata(pressao[frame] + terreno)
            texto_tempo.set_text(f'Tempo: {tempo[frame]:.2f} s')
            return linha_pressao, texto_tempo

        # Configuração para acelerar a renderização do GIF:
        # Se Nt for muito grande (ex: 5000), fazer o GIF frame por frame demora muito.
        # Alterando o passo (step_frames), controlamos a amostragem.
        step_frames = max(1, Nt // resolucao)
        frames_animacao = range(0, Nt, step_frames)

        print("Gerando a animação e salvando o arquivo GIF... Por favor, aguarde.")
        
        anim_p = FuncAnimation(
            fig1, 
            atualizar_p, 
            frames=frames_animacao, 
            interval=50,  # tempo em milissegundos entre cada frame na tela
            blit=True
        )

        nome_anim = f"animacao_caso_{caso_simulado}.gif"
        caminho_anim = os.path.join(pasta_saida, nome_anim)
        
        # Salva utilizando o 'pillow' como especificado
        anim_p.save(caminho_anim, writer="pillow", fps=20)
        plt.close(fig1)
        print(f"Animação salva com sucesso em: {caminho_anim}")