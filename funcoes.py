import copy
import pickle
import random

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


# Configurações para exibir todas as colunas e ajustar a largura
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 100)
pd.set_option('display.max_colwidth', None)

PORCENTAGEM_SELECAO = 0.5


def ler_arquivo(nomeArquivo, numTarefas, dicionarioTarefas):
    with open(nomeArquivo, 'r') as arquivo:
        # Itera sobre cada linha no arquivo
        i = 0
        for linha in arquivo:
            if i == 0:
                numTarefas = int(linha.strip()) + 2
            else:
                if linha.__contains__('#'):
                    continue
                linha = linha.strip().split(' ')
                linha_formatada = [valor for valor in linha if valor != '']
                dicionarioTarefas[linha_formatada[0]] = {
                    'tarefa': linha_formatada[0],
                    'tempo_execucao': linha_formatada[1],
                    'num_predecessores': linha_formatada[2],
                    'predecessores': linha_formatada[3:]
                }
            i += 1
    return numTarefas, dicionarioTarefas


def ler_numero_tarefas(nomeArquivo):
    with open(nomeArquivo, 'r') as arquivo:
        # Itera sobre cada linha no arquivo
        i = 0
        for linha in arquivo:
            if i == 0:
                substrings = linha.split()
                listaAux = [int(substring) for substring in substrings]
                numTarefas = listaAux[0]
                return numTarefas

        print('Erro ao ler o número de tarefas')
        return -1


def ler_arquivo_ghe(nomeArquivo, numProcessadores):

    dicionarioTarefas = {}

    try:

        with open(nomeArquivo, 'r') as arquivo:
            # Itera sobre cada linha no arquivo
            i = 0
            for linha in arquivo:

                if i == 0:
                    i += 1
                    continue

                linha = linha.strip().split(' ')
                linha_formatada = [valor for valor in linha if valor != '']
                # print(json.dumps(linha_formatada, indent=4))

                predecessores = []
                for predecessor in linha_formatada[numProcessadores+2::2]:
                    predecessores.append(predecessor)

                custosComunicacao = []
                for custoComunicacao in linha_formatada[numProcessadores+3::2]:
                    custosComunicacao.append(custoComunicacao)

                dicionarioTarefas[linha_formatada[0]] = {
                    'tarefa': linha_formatada[0],
                    'tempos_execucao': copy.deepcopy(linha_formatada[1:numProcessadores+1]),
                    'num_predecessores': copy.deepcopy(linha_formatada[numProcessadores+1]),
                    'predecessores': predecessores,
                    'custos_comunicacao': custosComunicacao
                }
                i += 1
                # print(json.dumps(dicionarioTarefas, indent=4))
        return dicionarioTarefas

    except Exception as e:
        print(f'Erro ao ler o arquivo {nomeArquivo}')
        print(e)
        return None


# def ler_arquivo_ghe(nomeArquivo, numProcessadores):

#     dicionarioTarefas = {}

#     with open(nomeArquivo, 'r') as arquivo:
#         # Itera sobre cada linha no arquivo
#         i = 0
#         for linha in arquivo:

#             if i == 0:
#                 i += 1
#                 continue

#             linha = linha.strip().split(' ')
#             linha_formatada = [valor for valor in linha if valor != '']
#             # print(json.dumps(linha_formatada, indent=4))
#             dicionarioTarefas[linha_formatada[0]] = {
#                 'tarefa': linha_formatada[0],
#                 'tempos_execucao': copy.deepcopy(linha_formatada[1:numProcessadores+1]),
#                 'num_predecessores': copy.deepcopy(linha_formatada[numProcessadores+1]),
#                 'predecessores': copy.deepcopy(linha_formatada[numProcessadores+2:numProcessadores+2+int(linha_formatada[numProcessadores+1])]),
#                 'custos_comunicacao': copy.deepcopy(linha_formatada[numProcessadores+2+int(linha_formatada[numProcessadores+1]):])
#             }
#             i += 1
#             # print(json.dumps(dicionarioTarefas, indent=4))
#     return dicionarioTarefas


def selecaoIndividuos(populacao, dicionarioTarefas, numProcessadores, numTarefas, tamanhoPopulacao):

    individuosSelecionados = []
    individuosSorteados = []
    while True:
        if len(individuosSelecionados) == int(tamanhoPopulacao * PORCENTAGEM_SELECAO):
            break

        individuo1 = None
        individuo2 = None

        while True:
            individuo1 = random.choice(populacao)
            if individuo1 not in individuosSorteados:
                individuosSorteados.append(individuo1)
                break

        while True:
            individuo2 = random.choice(populacao)
            if individuo2 not in individuosSorteados:
                individuosSorteados.append(individuo2)
                break

        fitness1 = fitness(individuo1, dicionarioTarefas,
                           numProcessadores, numTarefas)
        fitness2 = fitness(individuo2, dicionarioTarefas,
                           numProcessadores, numTarefas)

        if fitness1 < fitness2:
            individuosSelecionados.append(individuo1)
            continue

        individuosSelecionados.append(individuo2)

    return individuosSelecionados


def geraPrimeiraParteIndividuo(numProcessadores, numTarefas):
    primeiraParteIndividuo = []

    for _ in range(numTarefas):
        processador = random.randint(0, numProcessadores - 1)
        primeiraParteIndividuo.append(processador)

    return primeiraParteIndividuo


def geraSegundaParteIndividuo(numTarefas, dicionarioTarefas):
    segundaParteIndividuo = []

    while True:

        if len(segundaParteIndividuo) == numTarefas:
            break

        tarefa = str(random.randint(0, numTarefas - 1))

        if tarefa in segundaParteIndividuo:
            continue

        predecessores = dicionarioTarefas[tarefa]['predecessores']

        if len(predecessores) == 0:
            segundaParteIndividuo.append(tarefa)
            continue

        predecessorEstaNaLista = True
        for predecessor in predecessores:
            if predecessor not in segundaParteIndividuo:
                predecessorEstaNaLista = False

        if predecessorEstaNaLista:
            segundaParteIndividuo.append(tarefa)

    return segundaParteIndividuo


def populacaoInicial(numTarefas, numProcessadores, tamanhoPopulacao, dicionarioTarefas):
    populacao = []

    while True:

        if len(populacao) == tamanhoPopulacao:
            break

        individuo = {
            'mapeamento': geraPrimeiraParteIndividuo(numProcessadores, numTarefas),
            'sequencia': geraSegundaParteIndividuo(numTarefas, dicionarioTarefas)
        }

        if len(individuo['mapeamento']) > 0 and len(individuo['sequencia']) > 0 and individuo:
            # print(individuo)
            populacao.append(individuo)

    return populacao


def crossover_map(pai1, pai2, numTarefas):
    ponto_corte = random.randint(0, numTarefas - 1)
    filho1 = {
        'mapeamento': [],
        'sequencia': pai1['sequencia']
    }
    filho2 = {
        'mapeamento': [],
        'sequencia': pai2['sequencia']
    }

    filho1['mapeamento'] = pai1['mapeamento'][:ponto_corte] + \
        pai2['mapeamento'][ponto_corte:]

    filho2['mapeamento'] = pai2['mapeamento'][:ponto_corte] + \
        pai1['mapeamento'][ponto_corte:]

    return [filho1, filho2]


def crossover_seq(pai1, pai2, numTarefas):
    ponto_corte = random.randint(0, numTarefas - 1)
    filho = {
        'mapeamento': pai1['mapeamento'],
        'sequencia': []
    }

    tarefasCorte = pai1['sequencia'][:ponto_corte]
    filho['sequencia'] = tarefasCorte

    for tarefa in pai2['sequencia']:
        if tarefa not in tarefasCorte:
            filho['sequencia'].append(tarefa)

    return filho


def mutacao(pai, numeroProcessadores):
    posicao = random.randint(0, len(pai['sequencia']) - 1)

    while True:
        novoProcessador = random.randint(0, numeroProcessadores - 1)

        if novoProcessador != pai['mapeamento'][posicao]:
            pai['mapeamento'][posicao] = novoProcessador
            break

    return pai


def fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas):
    RT = [0] * numProcessadores  # RT = Ready Time
    ST = [0] * numTarefas  # ST = Start Time
    FT = [0] * numTarefas  # FT = Finish Time
    # LT = List of Tasks # LT = list(individuo['sequencia'])
    LT = list(individuo['sequencia'])
    S_length = 1

    for _ in range(numTarefas):
        if len(LT) == 0:  # if not LT:
            break
        tarefa = int(LT.pop(0))
        j = 0
        for j in range(numProcessadores):
            if individuo['mapeamento'][tarefa] == j:
                ST[tarefa] = max(RT[j], FT[tarefa])
                FT[tarefa] = ST[tarefa] + \
                    int(dicionarioTarefas[str(tarefa)]['tempo_execucao'])
                RT[j] = FT[tarefa]
            # j += 1

        S_length = max(FT)
        # i += 1
    a = 1
    return (a / S_length)


def cria_tempo_execucao(numProcessadores, tempoExecucaoSTG, variacaoExecucao):

    temposExecucao = ''

    if tempoExecucaoSTG == 0:
        for _ in range(numProcessadores):
            temposExecucao += '0    '
    else:
        for _ in range(numProcessadores):
            novoTempoExecucao = random.randint(
                tempoExecucaoSTG, tempoExecucaoSTG + variacaoExecucao)

            temposExecucao += f'{novoTempoExecucao}    '

    return temposExecucao


def cria_custo_comunicacao(tempoExecucaoSTG, numPredecessores, variacaoDados):

    custosComunicacao = ''

    if tempoExecucaoSTG == 0:
        for _ in range(numPredecessores):
            custosComunicacao += '0    '
    else:
        for _ in range(numPredecessores):

            custoComunicacao = 0

            if variacaoDados != 0:
                custoComunicacao = random.randint(1, variacaoDados)

            custosComunicacao += f'{custoComunicacao}    '

    return custosComunicacao


def writeFormatCol(data):
    colContent = str(data).rjust(11)
    return colContent


def escreve_ghe(dicionarioSTG, numProcessadores, variacaoExecucao, variacaoDados, nomeArquivo, numTarefas):

    f = open(nomeArquivo, 'w')

    # f.write(f'          {numTarefas-2}          {numProcessadores}')
    f.write(writeFormatCol(numTarefas-2))
    f.write(writeFormatCol(numProcessadores))
    f.write('\n')

    for chave in dicionarioSTG:
        tarefa = dicionarioSTG[chave]
        tempoExecucaoSTG = int(tarefa['tempo_execucao'])
        numPredecessores = int(tarefa['num_predecessores'])
        predecessores = tarefa['predecessores']

        # if (tempoExecucaoSTG == 0 and chave == '0'):
        #     f.write(f'{numTarefas}    {numProcessadores}')
        #     continue

        temposExecucao = cria_tempo_execucao(
            numProcessadores, tempoExecucaoSTG, variacaoExecucao)
        custosComunicacao = cria_custo_comunicacao(
            tempoExecucaoSTG, numPredecessores, variacaoDados)

        # predecessoresStr = ''

        # for predecessor in predecessores:
        #     predecessoresStr += f'{predecessor}    '

        f.write(writeFormatCol(tarefa["tarefa"]))
        for tempo in temposExecucao.split():
            f.write(writeFormatCol(tempo))

        f.write(writeFormatCol(numPredecessores))

        strAux = ''
        for (custoComunicacao, predecessor) in zip(custosComunicacao.split(), predecessores):
            strAux += f'{predecessor}    {custoComunicacao}    '
            f.write(writeFormatCol(predecessor))
            f.write(writeFormatCol(custoComunicacao))

        # f.write(
        #     f'\n{tarefa["tarefa"]}    {temposExecucao}{numPredecessores}    {strAux}')
        f.write('\n')

    f.close()


def salva_resultados(enderecoArquivo, dicionarioResultados):

    with open(enderecoArquivo, 'wb') as f:
        pickle.dump(dicionarioResultados, f)

    print('Resultados salvos com sucesso')


def carrega_resultados(enderecoArquivo):

    with open(enderecoArquivo, 'rb') as f:
        dicionarioResultados = pickle.load(f)

    return dicionarioResultados


def compare_algorithms(data):
    """
    Compara os resultados de makespan e load balance de diferentes algoritmos.

    Args:
        data: Dicionário com os resultados dos algoritmos.

    Returns:
        DataFrame: DataFrame com as métricas estatísticas para cada algoritmo.
    """

    results = []
    for algorithm, algorithm_data in data.items():
        makespans = []
        load_balances = []
        for num_tasks, graphs in algorithm_data.items():
            for graph, values in graphs.items():
                makespans.append(values['makespan'])
                load_balances.append(values['loadBalance'])

        results.append({
            'Algorithm': algorithm,
            'Makespan_Mean': np.mean(makespans),
            'Makespan_Std': np.std(makespans),
            'Makespan_Min': np.min(makespans),
            'Makespan_Max': np.max(makespans),
            'LoadBalance_Mean': np.mean(load_balances),
            'LoadBalance_Std': np.std(load_balances),
            'LoadBalance_Min': np.min(load_balances),
            'LoadBalance_Max': np.max(load_balances)
        })

    return pd.DataFrame(results)


def compare_algorithms2(data):
    """
    Compara os resultados de load balance e makespan dos diferentes algoritmos
    e retorna os resultados como um único DataFrame.

    Args:
    data (dict): Dicionário contendo os dados dos algoritmos, conforme a estrutura descrita.

    Returns:
    DataFrame: DataFrame contendo as comparações de makespan e load balance para cada par de algoritmos.
    """
    algorithms = list(data.keys())
    tasks = list(next(iter(data.values())).keys())
    graphs = list(next(iter(next(iter(data.values())).values())).keys())

    comparison_results = []

    for alg1 in algorithms:
        alg1_makespan_values = []
        alg1_loadBalance_values = []
        for task in tasks:
            for graph in graphs:
                if graph in data[alg1][task]:
                    alg1_makespan_values.append(
                        data[alg1][task][graph]['makespan'])
                    alg1_loadBalance_values.append(
                        data[alg1][task][graph]['loadBalance'])

        mean_makespan_alg1 = np.mean(alg1_makespan_values)
        std_makespan_alg1 = np.std(alg1_makespan_values)
        mean_loadBalance_alg1 = np.mean(alg1_loadBalance_values)
        std_loadBalance_alg1 = np.std(alg1_loadBalance_values)

        for alg2 in algorithms:
            if alg1 != alg2:
                alg2_makespan_values = []
                alg2_loadBalance_values = []
                for task in tasks:
                    for graph in graphs:
                        if graph in data[alg2][task]:
                            alg2_makespan_values.append(
                                data[alg2][task][graph]['makespan'])
                            alg2_loadBalance_values.append(
                                data[alg2][task][graph]['loadBalance'])

                if alg1_makespan_values and alg2_makespan_values:
                    stat_makespan, p_value_makespan = wilcoxon(
                        alg1_makespan_values, alg2_makespan_values)
                    stat_loadBalance, p_value_loadBalance = wilcoxon(
                        alg1_loadBalance_values, alg2_loadBalance_values)

                    comparison_results.append({
                        "Algorithm 1": alg1,
                        "Algorithm 2": alg2,
                        "Mean Makespan Alg1": mean_makespan_alg1,
                        "Std Makespan Alg1": std_makespan_alg1,
                        "Mean Makespan Alg2": np.mean(alg2_makespan_values),
                        "Std Makespan Alg2": np.std(alg2_makespan_values),
                        "Wilcoxon Makespan Stat": stat_makespan,
                        "Wilcoxon Makespan p-value": p_value_makespan,
                        "Mean LoadBalance Alg1": mean_loadBalance_alg1,
                        "Std LoadBalance Alg1": std_loadBalance_alg1,
                        "Mean LoadBalance Alg2": np.mean(alg2_loadBalance_values),
                        "Std LoadBalance Alg2": np.std(alg2_loadBalance_values),
                        "Wilcoxon LoadBalance Stat": stat_loadBalance,
                        "Wilcoxon LoadBalance p-value": p_value_loadBalance
                    })

    df_comparison = pd.DataFrame(comparison_results)

    return df_comparison


def save_dataframe_to_txt(df, filename):
    """
    Salva a estrutura de um DataFrame em um arquivo .txt.

    Args:
    df (pd.DataFrame): O DataFrame que você deseja salvar.
    filename (str): O caminho/nome do arquivo .txt onde o DataFrame será salvo.
    """
    # Convertendo o DataFrame para uma string formatada
    df_string = df.to_string(index=False)

    # Gravando a string formatada em um arquivo .txt
    with open(filename, 'w') as file:
        file.write(df_string)


def converte_grafos_reais_stg_em_ghe():
    basePath = 'grafos_reais/'

    listaArquivos = [f'{basePath}robot', f'{
        basePath}sparse', f'{basePath}fpppp']

    for arquivo in listaArquivos:

        dicionarioSTG = {}
        numTarefas = 0

        numTarefas, dicionarioSTG = ler_arquivo(
            f'{arquivo}.stg', numTarefas, dicionarioSTG)

        numProcessadoresLista = [2, 4, 8, 16]
        variacaoCustoComputacionalLista = [2, 20, 100]
        variacaoCustoComunicacaoLista = [0, 30, 100]

        for numProcessadores in numProcessadoresLista:
            for variacaoCustoComputacional in variacaoCustoComputacionalLista:
                for variacaoCustoComunicacao in variacaoCustoComunicacaoLista:
                    escreve_ghe(dicionarioSTG, numProcessadores, variacaoCustoComputacional, variacaoCustoComunicacao,
                                f'{arquivo}-{numProcessadores}-{variacaoCustoComputacional}-{variacaoCustoComunicacao}.stg', numTarefas)
