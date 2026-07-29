import numpy as np
import matplotlib.pyplot as plt
import os
import h5py as h5
import csv
from casos import casos

# --- Configurações Iniciais ---
pasta_saida = "resultados_graficos_h5"
os.makedirs(pasta_saida, exist_ok=True)
t_fonte = 35

# Constantes Físicas do Modelo (Idênticas ao script de simulação)
Lt = 1000                  
f = 0.02                   
g = 9.81                   
H0 = 10                    

print("Lendo os dados de simulação do arquivo HDF5...")

# --- Leitura dos Resultados de Pressão ---
max_pressures = []
with h5.File('dados_simulacao.h5', 'r') as hdf:
    for caso_simulado in range(len(casos)):
        nome_caso = f'caso_{caso_simulado}'
        pressao = hdf[nome_caso]['pressao'][:]
        max_pressures.append(np.max(pressao))

p0 = max_pressures[0]

# =====================================================================
# 1. RECONSTRUÇÃO DOS PARÂMETROS FÍSICOS & MATRIZ DE SENSIBILIDADE
# =====================================================================
print("Calculando variáveis físicas e Matriz de Sensibilidade...")

dados_fisicos = []
for i, caso in enumerate(casos):
    # Recálculo das variáveis exatas da simulação
    dx = caso[0]
    D_int = caso[1] / 1000
    c = 9900 / np.sqrt(48.3 + (caso[3] * (caso[1] / caso[2])))
    v0_calc = np.sqrt((H0 * 2 * g) / (1 + f * (Lt / D_int)))
    Tal = 2 * Lt / c
    TF_s = caso[4] * Tal
    
    dados_fisicos.append({
        'Caso': f'Caso {i}',
        'P_max (m.c.a)': p0 if i == 0 else max_pressures[i], # Força consistência visual no CSV
        'dx (m)': dx,
        'Diâmetro (m)': D_int,
        'Tempo Manobra (s)': TF_s,
        'Celeridade (m/s)': c,
        'Velocidade Inicial (m/s)': v0_calc
    })

# Variáveis base do Caso 0 para o cálculo percentual
base = dados_fisicos[0]

dados_matriz_csv = []
matriz_coef_csv = []
matriz_var = []

for i in range(len(casos)):
    atual = dados_fisicos[i]
    
    # Cálculo das variações percentuais em relação ao Caso 0
    delta_p = ((atual['P_max (m.c.a)'] - base['P_max (m.c.a)']) / base['P_max (m.c.a)']) * 100
    delta_dx = ((atual['dx (m)'] - base['dx (m)']) / base['dx (m)']) * 100
    delta_d = ((atual['Diâmetro (m)'] - base['Diâmetro (m)']) / base['Diâmetro (m)']) * 100
    delta_tf = ((atual['Tempo Manobra (s)'] - base['Tempo Manobra (s)']) / base['Tempo Manobra (s)']) * 100
    delta_c = ((atual['Celeridade (m/s)'] - base['Celeridade (m/s)']) / base['Celeridade (m/s)']) * 100
    delta_v0 = ((atual['Velocidade Inicial (m/s)'] - base['Velocidade Inicial (m/s)']) / base['Velocidade Inicial (m/s)']) * 100

    dados_matriz_csv.append({
        'Cenário': f"{atual['Caso']}",
        'P_max (m.c.a)[Δ%]': f"{atual['P_max (m.c.a)']:.2f} [{delta_p:+.2f}%]",
        'dx (m) [Δ%]': f"{atual['dx (m)']:.2f} [{delta_dx:+.2f}%]",
        'Diâmetro (m) [Δ%]': f"{atual['Diâmetro (m)']:.4f} [{delta_d:+.2f}%]",
        'Tempo Manobra (s) [Δ%]': f"{atual['Tempo Manobra (s)']:.2f} [{delta_tf:+.2f}%]",
        'Celeridade (m/s) [Δ%]': f"{atual['Celeridade (m/s)']:.2f} [{delta_c:+.2f}%]",
        'Velocidade (m/s) [Δ%]': f"{atual['Velocidade Inicial (m/s)']:.2f} [{delta_v0:+.2f}%]"
    })

    matriz_coef_csv.append({
        'Cenário': f"{atual['Caso']}",
        'dx': f"{delta_p/delta_dx:.2f}",
        'Diâmetro': f"{delta_p/delta_d:.2f}",
        'Tempo Manobra': f"{delta_p/delta_tf:.2f}",
        'Celeridade': f"{delta_p/delta_c:.2f}",
        'Velocidade Inicial': f"{delta_p/delta_v0:.2f}"
    })

    matriz_var.append({
        'Cenário': f"{atual['Caso']}",
        'ΔP_max (m.c.a)': delta_p,
        'Δdx (m)': delta_dx,
        'ΔDiâmetro (m)': delta_d,
        'ΔTempo Manobra (s)': delta_tf,
        'ΔCeleridade (m/s)': delta_c,
        'ΔVelocidade Inicial (m/s)': delta_v0
    })

caminho_csv = os.path.join(pasta_saida, "matriz_resumo.csv")
with open(caminho_csv, mode='w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=dados_matriz_csv[0].keys(), delimiter=';')
    writer.writeheader()
    writer.writerows(dados_matriz_csv)

caminho_csv = os.path.join(pasta_saida, "matriz_sensibilidade_coef.csv")
with open(caminho_csv, mode='w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=matriz_coef_csv[0].keys(), delimiter=';')
    writer.writeheader()
    writer.writerows(matriz_coef_csv)

with open(os.path.join(pasta_saida, "matriz_variacoes_percentuais.csv"), mode='w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=matriz_var[0].keys(), delimiter=';')
    writer.writeheader()
    writer.writerows(matriz_var)


print(f"Matriz de Sensibilidade Física salva em: {caminho_csv}")