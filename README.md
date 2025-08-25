# IC-AG
Trabalho sobre Algoritmo Genético para a Disciplina de Projeto de Graduação 2

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
- `--tamanho-populacao <int>`: tamanho da população usado no experimento. Se omitido, o CLI detecta automaticamente o tamanho a partir do arquivo salvo (PKL) carregado.
- `--iteracoes <int>`: número de iterações da evolução (ciclos do AG).
- `--alpha <float>[,<float>...]` (repetível): um ou mais valores de alpha a serem testados. Pode repetir a opção (`--alpha 0.5 --alpha 0.7`) ou passar como lista separada por vírgula (`--alpha 0.5,0.7`).
- `--cx-alloc <float>`: probabilidade de crossover na etapa de alocação (intervalo esperado: 0.0 a 1.0).
- `--cx-sched <float>`: probabilidade de crossover na etapa de escalonamento (0.0 a 1.0).
- `--mut-alloc <float>`: probabilidade de mutação na etapa de alocação (0.0 a 1.0).
- `--mut-sched <float>`: probabilidade de mutação na etapa de escalonamento (0.0 a 1.0).
- `--elitismo <float>`: taxa de elitismo aplicada a cada iteração (0.0 a 1.0).
- `--pasta-resultados <caminho>`: diretório base para salvar os CSVs. A estrutura final fica `<base>/<hash>/run_XXX/`, com `run_001`, `run_002`, ... gerados automaticamente por execução.

Subcomando `salvar-executar`:

- `--grafo <caminho.stg>`: caminho do grafo para gerar a população e executar o experimento.
- `--tamanho-populacao <int>`: tamanho da população inicial; se omitido, usa o padrão. Na execução, se omitido, pode ser inferido do PKL salvo.
- `--iteracoes <int>`: número de iterações.
- `--alpha <float>[,<float>...]`: valores de alpha (mesmas regras do subcomando `carregar`).
- `--cx-alloc <float>`: probabilidade de crossover de alocação.
- `--cx-sched <float>`: probabilidade de crossover de escalonamento.
- `--mut-alloc <float>`: probabilidade de mutação de alocação.
- `--mut-sched <float>`: probabilidade de mutação de escalonamento.
- `--elitismo <float>`: taxa de elitismo.
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

