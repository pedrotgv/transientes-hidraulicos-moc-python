# 🌊 Simulação de Transientes Hidráulicos (Golpe de Aríete) em Python

Este repositório contém o código-fonte desenvolvido como parte do meu Trabalho de Conclusão de Curso (TCC) em Engenharia Civil pela Universidade Federal de Uberlândia (UFU).

**Autor:** Pedro Thomaz Gonzales Viviani 

**Orientadora:** Prof. Alice Rosa da Silva 

**Coorientador:** Bruno de Oliveira Lázaro 

**Ano:** 2026 


## 📖 Sobre o Projeto

O objetivo deste trabalho é apresentar o desenvolvimento e a aplicação de um algoritmo computacional, implementado na linguagem Python, para análise de transientes hidráulicos em condutos forçados, com ênfase no fenômeno do golpe de aríete.

Utilizando o Método das Características (MOC), foram formuladas e discretizadas as equações da hidráulica, considerando condições de contorno típicas de sistemas de reservatório, tubo e válvula (RTV). A simulação, aplicada a um modelo de tubulação com fechamento brusco de válvula, gera resultados estáticos, em forma de gráficos, e dinâmicos, por meio de vídeos, evidenciando a propagação de ondas de pressão e as variações de vazão ao longo do tempo.

O estudo contribui para a compreensão e visualização do comportamento transitório em sistemas hidráulicos, oferecendo uma ferramenta de baixo custo, de fácil replicação e alinhada às recomendações normativas, com potencial para aplicação acadêmica.

## ⚙️ Funcionalidades do Código

* **Simulação de Múltiplos Cenários:** É possível definir uma lista de casos a serem simulados de forma sequencial, variando parâmetros como discretização espacial, diâmetro, espessura, material (ex: Aço, PVC) e o tempo de fechamento da válvula arquivo: [casos.py].
* **Cálculo da Celeridade da Onda:** O código calcula de forma autônoma a celeridade da onda de pressão com base nas características geométricas e propriedades físicas do tubo.
* **Linearização do Atrito:** Considera as perdas de carga distribuídas ao longo da tubulação durante a execução do Método das Características.
* **Geração de Gráficos:**
* **Gráfico (a):** Envoltórias de pressão máxima e mínima ao longo do comprimento da tubulação.
* **Gráfico (b):** Histórico de pressões no meio da tubulação em função do tempo.
* **Geração de Banco de dados hdp5:** O programa pode gerar um banco de dados, salvando os dados das simulações em um arquivo .h5 
* **Animações Dinâmicas:** Geração de GIFs mostrando a onda de pressão propagando-se pela tubulação ao longo do tempo arquivo[transiente-hidraulico-moc-animacao.py].
* **Exportação de Relatórios:** Exporta automaticamente uma tabela com os valores consolidados das pressões máximas e mínimas (`.csv`).

## 🚀 Como Utilizar

### 1. Pré-requisitos

Certifique-se de ter o Python instalado. O código utiliza as seguintes bibliotecas, que podem ser instaladas via `pip`:

```bash
pip install requirements.txt

```

Observação:É recomendado fazer a instalação das bibliotecas em um ambiente virtual
```bash
python -m venv venv
source venv/Scripts/activate

pip install requirements.txt
```

**Lembre-se de manter o pip sempre atualizado**
```bash
python -m pip install --upgrade pip

```

### 2. Configurando a Simulação

No script casos.py, você pode configurar os casos que deseja simular alterando a matriz `casos`. Cada caso consiste em uma lista com os seguintes parâmetros na respectiva ordem:
`[Dx (m), Di (mm), Espessura (mm), kt, TF (fração do período da tubulação), TT (s), Material]`

Para habilitar a geração dos vídeos da propagação da onda (arquivos `.gif`), altere a variável `animacao` no início do código [transiente-hidraulico-moc-animacao.py] para `True`:


*Aviso: Habilitar a animação exigirá um maior poder de processamento e aumentará o tempo total da simulação.*

### 3. Execução

Execute o script Python pelo terminal:

```bash
python nome_do_arquivo.py

```

O programa criará automaticamente um arquivo chamado 'dados_simulacao.h5' no mesmo diretório em que o script está sendo executado. Todos os resultados serão salvos dentro desse arquivo.
Para obter os gráficos e o resumo das pressões a partir de um banco de dados .h5 basta executar o script transiente-hidraulico-moc-slicing-graficos-hdp5.py


## 📊 Estrutura dos Resultados

* `caso_X(a).png`: Gráfico da envoltória de pressões (máximas e mínimas) ao longo da tubulação para o caso simulado.
* `caso_X(b).png`: Gráfico do comportamento da pressão no tempo (avaliado no meio do tubo).
* `animacao_caso_X.gif`: Animação da propagação da onda de pressão (caso ativada nas configurações).
* `resumo_pressao.csv`: Tabela sumarizada com as pressões máximas e mínimas absolutas de todos os casos.

## 📊 Estrutura do banco de dados (`dados_simulacao.h5`)
* **Grupo 0** - Contém os dados da simulação do caso 0
    * **datasheet** - Pressão
    * **datasheet** - Vazão
    * **datasheet** - Tempo
    * **datasheet** - Posição_x
    * **datasheet** - Tabela de máximos
    * **datasheet** - Terreno
    * **Atributos** - São salvos os dados: [Dx], [Di], [e], [kt], [TF], [TT], [material] e [Lt]
... São criados um grupo por simulação e todos são salvos no mesmo arquivo dados_simulacao.h5

