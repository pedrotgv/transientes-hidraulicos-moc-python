import numpy as np
import os
from tqdm import tqdm
import time
import h5py as h5
from casos import casos


tempo_casos = []        # Matriz para simular o tempo dos casos
tabela_maximos = []     # Tabela para armazenar os valores de máximos e mínimos de cada simulação
cota_terreno = 0        # Define uma cota para a tubulação horizontal


with h5.File('dados_simulacao.h5', 'w') as hdf:

    for caso_simulado in tqdm(range(len(casos)), desc="Simulando casos"):     # Inicia a simulação de cada caso, gerenciando o tempo de simulação
        
        nome_caso = f'caso_{caso_simulado}'
        grupo_atual = hdf.create_group(nome_caso)    # Cria um grupo para cada caso simulado no arquivo HDF5

        t_inicio = time.time()    # Inicia o monitoramento de tempo da simulação total

        # --- DADOS SIMULAÇÃO ---
        Lt = 1000                  # Comprimento da tubulação [m]
        f = 0.02                   # Fator de atrito
        g = 9.81                   # Gravidade [m/s²]
        H0 = 10                    # Nível do reservatório [m]

        Dx = casos[caso_simulado][0]                    # Discretização espacial [m]
        D = round(casos[caso_simulado][1]/1000,2)       # Diâmetro Tubulação [m]

        c = 9900/np.sqrt(48.3+(casos[caso_simulado][3]*(casos[caso_simulado][1]/casos[caso_simulado][2])))  # Celeridade Tubulação [m/s]

        TT = casos[caso_simulado][5]                    # Tempo total de simulação [s]
        material = casos[caso_simulado][6]              # Nome do material

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
                    
            tempo.append(t*Dt)     # Insere o valor do tempo em uma tabela para gerar os gráficos (Eixo x)      

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
            
            # Cálculo final da Vazão (Qp)
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
        envol_max = np.max(pressao, axis=0)                    # Matriz de pressões com o maior valor de cada ponto.
        envol_min = np.min(pressao, axis=0)                    # Matriz de pressões com o menor valor de cada ponto.
        coluna_v_final = vazao[:, Nx]                          # Última coluna da matriz de vazão.
        coluna_m_pressao = pressao[:, pressao.shape[1] // 2]   # Coluna do meio da matriz de vazão

        tabela_maximos.append([caso_simulado, np.max(pressao),np.min(pressao)]) # Tabela com os valores para acesso rápido.

        grupo_atual.create_dataset('pressao', data=pressao, compression='gzip')   # Armazena a matriz de pressão da simulação no arquivo HDF5
        grupo_atual.create_dataset('vazao', data=vazao, compression='gzip')       # Armazena a matriz de vazão da simulação no arquivo HDF5
        grupo_atual.create_dataset('tempo', data=tempo, compression='gzip')       # Armazena a matriz de tempo da simulação no arquivo HDF5
        grupo_atual.create_dataset('posicao_x', data=x, compression='gzip')   # Armazena a matriz de posicao x da simulação no arquivo HDF5
        grupo_atual.create_dataset('tabela_maximos', data=np.array(tabela_maximos), compression='gzip')   # Armazena a tabela de valores máximos e mínimos da simulação no arquivo HDF5
        grupo_atual.create_dataset('terreno', data=terreno, compression='gzip')   # Armazena a tabela de valores máximos e mínimos da simulação no arquivo HDF5
        grupo_atual.attrs['Dx'] = Dx
        grupo_atual.attrs['Di'] = D
        grupo_atual.attrs['e'] = casos[caso_simulado][2]
        grupo_atual.attrs['kt'] = casos[caso_simulado][3]
        grupo_atual.attrs['TF'] = casos[caso_simulado][4]
        grupo_atual.attrs['TT'] = casos[caso_simulado][5]
        grupo_atual.attrs['Material'] = material
        grupo_atual.attrs['Lt'] = Lt
        

        t_fim = time.time()    # Finaliza o monitoramento de tempo da simulação total

print(f"Tempo total de simulação: {t_fim - t_inicio:.2f} segundos")
