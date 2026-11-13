# IC-AG: algoritmo genético para escalonamento de tarefas

Código do Trabalho de Conclusão de Curso **"Algoritmo genético para escalonamento de tarefas em ambientes paralelos heterogêneos"** (Ciência da Computação, Universidade Federal de Uberlândia, 2024), de John Vítor da Silva Cunha, com orientação do Prof. Paulo Henrique Ribeiro Gabriel.

- Monografia: https://repositorio.ufu.br/handle/123456789/44002
- Branch com o código do TCC: `tcc`

## O que é

Um algoritmo genético em Python que escalona tarefas de grafos de dependência (DAGs) em multiprocessadores heterogêneos, com custo de comunicação entre processadores. A aptidão combina **makespan** e **balanceamento de carga** (*load balance*), ponderados por um parâmetro `alpha`.

O trabalho compara o algoritmo genético com quatro algoritmos determinísticos (HEFT, CPOP, IHEFT e IPEFT) em três aplicações reais (`robot`, `sparse` e `fpppp`). Os resultados e a discussão estão na monografia.

Depois da entrega do TCC, o projeto foi estendido a pedido do orientador com:

- um segundo experimento, que compara a primeira população com a última;
- carga e gravação de populações iniciais, para repetir experimentos sobre a mesma população;
- uma interface gráfica e uma linha de comando (CLI) com semente aleatória, para execuções reproduzíveis.

## Estrutura

| Arquivo ou pasta | Função |
| --- | --- |
| `MSE.py` | Algoritmo genético (classe `MSE`): população, seleção, cruzamento, mutação, elitismo e aptidão |
| `funcoes.py` | Leitura de grafos, operadores, métricas (makespan, load balance) e gravação de populações e resultados |
| `main.py` | Primeiro experimento: algoritmo genético contra os algoritmos determinísticos (com janela de parâmetros) |
| `main2.py`, `main2_gui.py`, `main2_cli.py` | Segundo experimento, comparando primeira e última população (código, interface gráfica e CLI) |
| `task_scheduling.py` | Implementação dos algoritmos determinísticos de comparação (ver Créditos) |
| `analise_escalonamento.py`, `analise_iteracao.py`, `comparar_populacoes.py` | Validação dos escalonamentos e comparação dos resultados |
| `grafos_reais/`, `grafos_experimento/`, `grafos_gerados_dos_reais/` | Grafos (.stg) usados nos experimentos |
| `run*.sh`, `run*.bat` | Scripts que criam o ambiente virtual, instalam as dependências e abrem a interface |

## Como executar

Requisitos: Python 3.12 (versão usada no TCC) e `tkinter` para as interfaces gráficas.

```bash
python -m venv venv
source venv/bin/activate        # no Windows: venv\Scripts\activate
pip install -r requirements.txt
python main2_gui.py             # ou: python main.py, ou o CLI descrito abaixo
```

No Linux, instale o `tkinter` com `sudo apt-get install python3-tk`. Os scripts `run*.sh` e `run*.bat` fazem esses passos automaticamente.

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

