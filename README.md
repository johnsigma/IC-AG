# IC-AG: algoritmo genético para escalonamento de tarefas

Código do Trabalho de Conclusão de Curso **"Algoritmo genético para escalonamento de tarefas em ambientes paralelos heterogêneos"** (Ciência da Computação, Universidade Federal de Uberlândia, 2024), de John Vítor da Silva Cunha, com orientação do Prof. Paulo Henrique Ribeiro Gabriel.

- Monografia: https://repositorio.ufu.br/handle/123456789/44002
- Branch com o código do TCC: `tcc`

## O que é

Um algoritmo genético em Python que escalona tarefas de grafos de dependência (DAGs) em multiprocessadores heterogêneos, com custo de comunicação entre processadores. A aptidão combina **makespan** e **balanceamento de carga** (*load balance*), ponderados por um parâmetro `alpha`.

O trabalho compara o algoritmo genético com quatro algoritmos determinísticos (HEFT, CPOP, IHEFT e IPEFT) em três aplicações reais (`robot`, `sparse` e `fpppp`). Os resultados e a discussão estão na monografia.

## Extensão pós-TCC: experimento de populações

Depois da entrega do TCC, o projeto foi estendido a pedido do orientador (commits de fevereiro a agosto de 2025) com um segundo experimento. Em vez de comparar o algoritmo genético com os determinísticos, ele acompanha **o que acontece com uma população específica ao longo das gerações**: compara a população inicial com a população final da mesma execução.

### Como o experimento funciona

1. **Gerar e salvar a população inicial.** Dado um grafo (`.stg`) e um tamanho, a população é gerada e gravada em `populacoes/populacao_<hash>.pkl`. O nome do arquivo é o hash SHA-256 do conteúdo, que identifica a população.
2. **Carregar e conferir.** Ao carregar uma população pelo hash, o hash do conteúdo é recalculado e comparado, para garantir que é exatamente a mesma população. Assim é possível repetir o experimento, com outros parâmetros, partindo das mesmas condições iniciais.
3. **Evoluir.** O algoritmo genético (cruzamento e mutação sobre alocação e escalonamento, seleção por roleta e elitismo) roda por um número configurável de iterações, uma vez para cada valor de `alpha` informado.
4. **Registrar.** Para cada indivíduo da primeira e da última iteração são gravados, em CSV, as métricas, a aptidão, a alocação (tarefa → processador) e o escalonamento (ordem das tarefas). Os parâmetros da execução ficam no topo do mesmo arquivo.
5. **Reaproveitar.** A população final também é salva (com o próprio hash), para servir de ponto de partida de outro experimento.

### Métricas registradas por indivíduo

| Métrica | O que mede |
| --- | --- |
| Makespan | Maior tempo de processamento acumulado entre os processadores, incluindo comunicação |
| Load balance | Makespan dividido pelo tempo médio de processamento por processador (quanto mais perto de 1, mais equilibrado) |
| Flowtime | Soma dos tempos de término de todas as tarefas |
| Communication cost | Soma dos custos de comunicação entre tarefas dependentes alocadas em processadores diferentes |
| Waiting time | Soma do tempo que cada tarefa espera entre o fim de sua última predecessora e o próprio início |
| Fitness | `alpha × makespan + (1 − alpha) × load balance` |

Com a correção de agosto de 2025, todas as métricas são calculadas antes da aptidão, então a função de fitness pode combinar qualquer uma delas.

### Resultados e validação

- Cada execução grava em `resultados2/<hash>/run_XXX/` (numeração incremental por população), com `primeira_iteracao_<alpha>.csv` e `ultima_iteracao_<alpha>.csv`. Execuções anteriores nunca são sobrescritas.
- Com a mesma semente (`--seed`), o experimento é reproduzível: a mesma semente gera a mesma população (mesmo hash) e a mesma população final.
- Dois scripts de apoio conferem os resultados (veja o passo a passo da extensão):
  - `analise_iteracao.py` valida se cada escalonamento gravado é possível (tarefas fictícias de início e fim nas posições certas, todas as tarefas presentes e cada uma depois de suas predecessoras) e mostra o percentual de indivíduos válidos e inválidos;
  - `verificar_dados.py` confere se a população salva em `.pkl` é idêntica à registrada no CSV da primeira iteração.

## Estrutura

| Arquivo ou pasta | Função |
| --- | --- |
| `MSE.py` | Algoritmo genético (classe `MSE`): população, seleção, cruzamento, mutação, elitismo e aptidão |
| `funcoes.py` | Leitura de grafos, operadores, métricas (makespan, load balance) e gravação de populações e resultados |
| `main.py` | Primeiro experimento: algoritmo genético contra os algoritmos determinísticos (com janela de parâmetros) |
| `main2.py`, `main2_gui.py`, `main2_cli.py` | Experimento de populações (lógica, interface gráfica e CLI) |
| `task_scheduling.py` | Implementação dos algoritmos determinísticos de comparação (ver Créditos) |
| `analise_iteracao.py`, `verificar_dados.py` | Validação dos escalonamentos gravados e conferência da população salva (usados no passo a passo da extensão) |
| `analise_escalonamento.py`, `comparar_populacoes.py` | Scripts de apoio usados durante o desenvolvimento, com os caminhos dos arquivos escritos no fim de cada arquivo |
| `grafos_reais/`, `grafos_experimento/`, `grafos_gerados_dos_reais/` | Grafos (.stg) usados nos experimentos |
| `run*.sh`, `run*.bat` | Scripts que criam o ambiente virtual, instalam as dependências e abrem a interface |

## Passo a passo

Todos os comandos devem ser executados na pasta raiz do repositório, porque os caminhos dos grafos (`grafos_experimento/...`) e das pastas de resultados são relativos a ela.

### 0. Preparação (uma vez)

```bash
git clone https://github.com/johnsigma/IC-AG.git
cd IC-AG
git checkout tcc                 # se a branch padrão ainda não for a tcc
python3.12 -m venv venv          # no Windows: python -m venv venv
source venv/bin/activate         # no Windows: venv\Scripts\activate
pip install -r requirements.txt
```

- O projeto foi desenvolvido e testado com **Python 3.12**; as versões das bibliotecas estão fixadas em `requirements.txt`.
- O `tkinter` só é necessário para as interfaces gráficas. Ele já vem com o Python no Windows e no macOS; no Linux, instale com `sudo apt-get install python3-tk`.
- Os scripts `run*.sh` (Linux) e `run*.bat` (Windows) fazem a preparação e executam o programa de uma vez. Os `.sh` também rodam `sudo apt-get`.

### 1. Versão do TCC: algoritmo genético contra HEFT, CPOP, IHEFT e IPEFT

Roda o experimento da monografia nos três grafos (`robot-4-20-30`, `sparse-4-100-30` e `fpppp-8-20-30`, que têm 90, 98 e 336 tarefas). Para cada grafo, o algoritmo genético é executado 9 vezes para cada valor de `alpha` (0, 0,25, 0,5, 0,75 e 1), e o resultado é comparado com o dos algoritmos determinísticos. Os parâmetros do algoritmo são: população de 20 indivíduos, 200 iterações, probabilidade de cruzamento de 0,4 (alocação e escalonamento), de mutação de 0,2 (alocação e escalonamento) e taxa de elitismo de 0,2.

**Pela linha de comando**

```bash
python main.py
```

(ou `./run.sh` no Linux, `run.bat` no Windows). O programa mostra o andamento de cada grafo no terminal. A execução completa leva cerca de 40 minutos, quase todo no grafo `fpppp` (medido em um computador comum; depende do processador). Para mudar os parâmetros nesse modo, edite o dicionário `parametrosMSE` na função `main` de `main.py`.

**Pela interface gráfica**

```bash
python main.py --gui
```

(ou `./run_gui.sh` ou `run_gui.bat`). Abre a janela **Parâmetros MSE**, com os campos tamanho da população, número de iterações, chances de cruzamento e de mutação (alocação e escalonamento) e taxa de elitismo. Altere o que quiser, clique em **Iniciar experimento** e acompanhe o andamento na área de texto da própria janela. É o mesmo experimento da linha de comando, com os parâmetros que você digitou. Os valores de `alpha`, os grafos e as 9 repetições são fixos.

**Resultado (nos dois modos)**

- `resultados/<grafo>_<id>.csv`: um arquivo por grafo. À esquerda ficam os parâmetros usados. À direita, uma linha para cada algoritmo: IPEFT, IHEFT, CPOP e HEFT (uma execução cada) e `MSE_<alpha>` (média de 9 execuções do algoritmo genético), com makespan, load balance, média e desvio padrão da iteração em que o melhor indivíduo foi encontrado, e desvios padrão do makespan e do load balance.
- `resultados/tempo_<id>.txt`: tempo total da execução.
- Não há semente aleatória nesta versão, então os números variam um pouco a cada execução.

### 2. Extensão: experimento de populações

A extensão trabalha em duas etapas: primeiro gera e salva uma população inicial, depois a carrega pelo hash e a evolui. O grafo informado ao carregar precisa ser o mesmo usado para gerar a população (o arquivo `.pkl` não guarda essa informação).

**Pela linha de comando**

1. Gere e salve uma população (anote o hash impresso no final):

   ```bash
   python main2_cli.py salvar --grafo grafos_experimento/robot-4-20-30.stg --tamanho-populacao 10 --seed 42
   ```

2. Carregue a população pelo hash e rode o experimento (aqui, 100 iterações e dois valores de `alpha`):

   ```bash
   python main2_cli.py carregar --hash <HASH> --grafo grafos_experimento/robot-4-20-30.stg --iteracoes 100 --alpha 0.5,0.7 --seed 42
   ```

   Para os dois passos de uma vez, use `salvar-executar` (mesmos argumentos). Todos os argumentos estão descritos na seção [CLI](#cli-main2_clipy).

3. Veja os resultados em `resultados2/<HASH>/run_001/`: `primeira_iteracao_<alpha>.csv` (população inicial) e `ultima_iteracao_<alpha>.csv` (população final). Cada linha é um indivíduo, com as cinco métricas, a aptidão, a alocação e o escalonamento. Os hashes das populações finais aparecem no terminal.

4. Confira os resultados (opcional):

   ```bash
   python analise_iteracao.py resultados2/<HASH>/run_001/ultima_iteracao_0.5.csv
   python verificar_dados.py <HASH>
   ```

   O primeiro informa quantos indivíduos têm escalonamento válido (o esperado é 100%). O segundo confirma que a população salva é idêntica à registrada na primeira iteração.

**Pela interface gráfica**

```bash
python main2_gui.py
```

(ou `./run2_gui.sh` ou `run2_gui.bat`). A janela tem duas abas.

1. **Aba "1. Gerenciar População"**
   - Em *Gerar Nova População*, informe o tamanho e o arquivo de grafo (use **Selecionar...** para escolher um `.stg`) e clique em **Gerar e Salvar População**. A população é salva, aparece uma mensagem com o hash e ela já fica carregada.
   - Para usar uma população salva antes, use **Carregar de Arquivo (.pkl)** ou **Carregar por Hash**. Confira se o arquivo de grafo continua sendo o mesmo da população.
2. **Aba "2. Executar Experimento"**
   - Em *Status da População* aparece o hash da população carregada.
   - Ajuste o número de iterações, as chances de cruzamento e de mutação e a taxa de elitismo (padrões da interface gráfica: 100 iterações e elitismo de 0,1) e informe os valores de `alpha` separados por vírgula, por exemplo `0.5, 0.7`.
   - Clique em **Rodar Experimento**. A janela fica sem responder enquanto o experimento roda. Ao final, uma mensagem mostra os hashes das populações finais.
3. Os resultados ficam em `resultados2/<hash>/run_XXX/`, como na linha de comando, e podem ser conferidos com os dois scripts do passo 4 acima.

## Créditos

- O projeto surgiu de um trabalho em grupo da disciplina de Inteligência Computacional, feito por John Cunha e Marcus Vinícius Torres. O repositório original é o [IC-AG](https://github.com/marcustorres02/IC-AG), do qual este é um fork. A evolução para o TCC (operadores, métricas, comparação com os algoritmos determinísticos, interfaces e experimentos) foi desenvolvida por John.
- Os algoritmos determinísticos de comparação em `task_scheduling.py` vêm do projeto [Task-Scheduling](https://github.com/Brenocsc/Task-Scheduling), de Breno.
- Os grafos reais (`robot`, `sparse` e `fpppp`) são da biblioteca de grafos da Waseda University, citada na monografia.

## CLI (main2_cli.py)

Este repositório agora inclui um CLI para rodar as funcionalidades de geração de população, carregamento e execução de experimentos em uma única linha de comando, sem alterar o `main2.py` original.

### Instalação de dependências

Ative seu ambiente virtual (opcional) e instale os requisitos:

```powershell
pip install -r .\requirements.txt
```

### Comandos

1) Salvar (gera e salva uma população; imprime o hash gerado):

```powershell
python .\main2_cli.py salvar --grafo grafos_experimento\robot-4-20-30.stg --tamanho-populacao 10
```

2) Carregar (carrega uma população por hash e executa o experimento):

```powershell
python .\main2_cli.py carregar --hash <HASH> --grafo grafos_experimento\robot-4-20-30.stg --iteracoes 10 --alpha 0.5,0.7 --cx-alloc 0.4 --cx-sched 0.4 --mut-alloc 0.2 --mut-sched 0.2 --elitismo 0.2
```

3) Salvar e executar em sequência (gera a população e já executa o experimento):

```powershell
python .\main2_cli.py salvar-executar --grafo grafos_experimento\robot-4-20-30.stg --iteracoes 10 --alpha 0.5,0.7 --tamanho-populacao 10
```

### Reprodutibilidade (seed)

Você pode passar uma seed para garantir reprodutibilidade (afeta numpy e random):

```powershell
python .\main2_cli.py salvar --grafo grafos_experimento\robot-4-20-30.stg --tamanho-populacao 10 --seed 42
```

### Parâmetros do AG

Há dois modos de definir parâmetros:

- Editar diretamente os dicionários no topo do arquivo `main2_cli.py`:
	- `DEFAULT_PARAM_POPULACAO` (ex.: `tamanhoPopulacao`, `grafo`)
	- `DEFAULT_PARAM_MSE` (ex.: `numeroIteracoes`, `chanceCrossoverAlocacao`, `chanceMutacaoAlocacao`, `taxaElitismo`, etc.)
	- `DEFAULT_ALPHAS` para os alphas padrão

- Sobrescrever via linha de comando (recomendado para automação):
	- `--iteracoes`, `--alpha`, `--tamanho-populacao`, `--cx-alloc`, `--cx-sched`, `--mut-alloc`, `--mut-sched`, `--elitismo`, `--pasta-resultados`, etc.

### Dicas

- Use `--verbose` para obter logs detalhados.
- Use `--seed` para reprodutibilidade.
- Os resultados (CSVs) são salvos por execução em `resultados2/<hash_populacao>/run_XXX/` por padrão (numeração incremental por hash).
- Para ver ajuda geral: `python .\main2_cli.py --help`
- Para ver a documentação rápida no terminal: `python .\main2_cli.py docs`

### Argumentos e significados

Argumentos globais (válidos para qualquer subcomando):

- `--verbose`: habilita logs detalhados (nível DEBUG).
- `--seed <int>`: define a semente para os geradores aleatórios (`numpy` e `random`) para tornar os resultados reprodutíveis.

Subcomando `salvar`:

- `--grafo <caminho.stg>`: caminho do arquivo de grafo (.stg) utilizado para gerar a população inicial. Se omitido, usa o padrão definido no código.
- `--tamanho-populacao <int>`: número de indivíduos da população inicial. Se omitido, usa o padrão definido no código.

Subcomando `carregar`:

- `--hash <str>` (obrigatório): identificador (hash) da população previamente salva que será carregada do disco.
- `--grafo <caminho.stg>`: caminho do arquivo de grafo (.stg) correspondente ao experimento. Se omitido, usa o padrão definido no código.
- `--iteracoes <int>`: número de iterações da evolução (ciclos do AG).
- `--alpha <float>[,<float>...]` (repetível): um ou mais valores de alpha a serem testados. Pode repetir a opção (`--alpha 0.5 --alpha 0.7`) ou passar como lista separada por vírgula (`--alpha 0.5,0.7`).
- `--cx-alloc <float>`: probabilidade de crossover no vetor de alocação (intervalo esperado: 0.0 a 1.0).
- `--cx-sched <float>`: probabilidade de crossover no vetor de escalonamento (0.0 a 1.0).
- `--mut-alloc <float>`: probabilidade de mutação no vetor de alocação (0.0 a 1.0).
- `--mut-sched <float>`: probabilidade de mutação no vetor de escalonamento (0.0 a 1.0).
- `--elitismo <float>`: taxa de elitismo aplicada a cada iteração (0.0 a 1.0).
- `--pasta-resultados <caminho>`: diretório base para salvar os CSVs. A estrutura final fica `<base>/<hash>/run_XXX/`, com `run_001`, `run_002`, ... gerados automaticamente por execução.

Subcomando `salvar-executar`:

- `--grafo <caminho.stg>`: caminho do grafo para gerar a população e executar o experimento.
- `--tamanho-populacao <int>`: tamanho da população inicial; se omitido, usa o padrão. Na execução, se omitido, pode ser inferido do PKL salvo.
- `--iteracoes <int>`: número de iterações.
- `--alpha <float>[,<float>...]`: valores de alpha (mesmas regras do subcomando `carregar`).
- `--cx-alloc <float>`: probabilidade de crossover no vetor de alocação (intervalo esperado: 0.0 a 1.0).
- `--cx-sched <float>`: probabilidade de crossover no vetor de escalonamento (0.0 a 1.0).
- `--mut-alloc <float>`: probabilidade de mutação no vetor de alocação (0.0 a 1.0).
- `--mut-sched <float>`: probabilidade de mutação no vetor de escalonamento (0.0 a 1.0).
- `--elitismo <float>`: taxa de elitismo aplicada a cada iteração (0.0 a 1.0).
- `--pasta-resultados <caminho>`: diretório base de resultados. Os arquivos são gravados em `<base>/<hash>/run_XXX/` para evitar sobrescritas entre execuções.

### Estrutura de resultados e versionamento

Para evitar sobrescrever resultados ao executar múltiplos experimentos para a mesma população (mesmo hash), os CSVs agora são salvos em subpastas por execução dentro da pasta do hash:

```
resultados2/
	<hash>/
		run_001/
			primeira_iteracao_0.5.csv
			ultima_iteracao_0.5.csv
			...
		run_002/
			primeira_iteracao_0.5.csv
			ultima_iteracao_0.5.csv
			...
```

- A numeração `run_XXX` é incremental por hash (run_001, run_002, ...), gerada automaticamente a cada execução.
- Você pode trocar o diretório base com `--pasta-resultados <caminho>` no CLI; a estrutura interna por hash e por execução é mantida.
- A mesma lógica vale para a interface gráfica (GUI), que usa a mesma função de experimento.

Subcomando `docs`:

- Não possui argumentos adicionais; imprime um guia rápido de uso e exemplos.

