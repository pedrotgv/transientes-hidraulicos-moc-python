# Simulação de Transientes Hidráulicos com o Método das Características (MOC)

Este repositório contém o código desenvolvido para o Trabalho de Conclusão de Curso *“Análise de Transientes Hidráulicos com o Método das Características e Simulação Computacional em Python”*, que implementa uma simulação completa do fenômeno do *golpe de aríete* em uma tubulação pressurizada.

A rotina numérica aplica o *Método das Características (MOC)* para resolver as equações da continuidade e da quantidade de movimento em regime transitório, permitindo o cálculo da pressão e da vazão ao longo da tubulação ao longo do tempo.

---

## 📌 Objetivos do código

- Modelar um sistema simples composto por *reservatório – tubulação – válvula*.
- Simular o fechamento progressivo da válvula e os efeitos do golpe de aríete.
- Calcular a evolução temporal da *pressão* e *vazão* em cada ponto da tubulação.
- Gerar:
  - Envoltórias de pressão  
  - Gráficos de vazão e pressão em pontos específicos  
  - Animação da propagação de pressão ao longo do tubo  

---

## 📐 Formulação Matemática

O código implementa as equações do Método das Características:

- Linhas características *C+* e *C−*
- Cálculo de `cp`, `cn`, `Ca` e `k`
- Atualização da pressão e vazão para cada nó da malha ao longo do tempo
- Inclusão das condições de contorno de:
  - Reservatório (pressão fixa)
  - Válvula (fechamento linear ao longo do tempo)

---

## 🧮 Parâmetros principais

Todos os parâmetros estão definidos no início do código e podem ser alterados conforme necessidade:

| Parâmetro | Significado | Valor padrão |
|----------|-------------|--------------|
| `Lt` | Comprimento da tubulação (m) | 1000 |
| `Dx` | Discretização espacial (m) | 1 |
| `D` | Diâmetro interno (m) | 1 |
| `f` | Fator de atrito | 0.02 |
| `H0` | Carga no reservatório (m.c.a) | 10 |
| `c` | Celeridade da onda (m/s) | 1000 |
| `TF` | Tempo de fechamento da válvula (s) | `Tal` |

O usuário pode modificar facilmente estes valores para estudar diferentes cenários.

---

## 📊 Resultados gerados pelo programa

O código produz:

### *1. Envoltória de Pressões*
Mostra os valores máximos e mínimos obtidos em cada ponto da tubulação.

### *2. Pressão no meio da tubulação ao longo do tempo*
Permite observar oscilações, amortecimento e comportamento transitório.

### *3. Vazão na válvula*
Exibe o fechamento da válvula e suas repercussões na vazão.

### *4. Vazão no meio da tubulação*
Útil para visualizar inversões e oscilações de fluxo.

### *5. Animação da propagação de pressão*
O gráfico dinamiza a variação espacial e temporal da pressão.


