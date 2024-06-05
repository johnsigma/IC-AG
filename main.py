import copy
import json
import random

# random.seed(675)

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


def ler_arquivo_ghe(nomeArquivo, numProcessadores):

    dicionarioTarefas = {}

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
            dicionarioTarefas[linha_formatada[0]] = {
                'tarefa': linha_formatada[0],
                'tempos_execucao': copy.deepcopy(linha_formatada[1:numProcessadores+1]),
                'num_predecessores': copy.deepcopy(linha_formatada[numProcessadores+1]),
                'predecessores': copy.deepcopy(linha_formatada[numProcessadores+2:numProcessadores+2+int(linha_formatada[numProcessadores+1])]),
                'custos_comunicacao': copy.deepcopy(linha_formatada[numProcessadores+2+int(linha_formatada[numProcessadores+1]):])
            }
            i += 1
            # print(json.dumps(dicionarioTarefas, indent=4))
    return dicionarioTarefas


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
            custoComunicacao = random.randint(1, variacaoDados)
            custosComunicacao += f'{custoComunicacao}    '

    return custosComunicacao


def escreve_ghe(dicionarioSTG, numProcessadores, variacaoExecucao, variacaoDados, nomeArquivo, numTarefas):

    f = open(f'{nomeArquivo[0:-4]}.txt', 'w')

    f.write(f'{numTarefas-2}    {numProcessadores}')

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

        predecessoresStr = ''

        for predecessor in predecessores:
            predecessoresStr += f'{predecessor}    '

        f.write(f'\n{tarefa['tarefa']}    {temposExecucao}{
                numPredecessores}    {predecessoresStr}{custosComunicacao}')

    f.close()


if __name__ == '__main__':
    dicionarioTarefas = {}
    numTarefas = 0

    # arquivo = input('Digite o nome do arquivo: ')
    arquivo = 'robot.stg'
    numProcessadores = int(input('Digite o número de processadores: '))
    # numeroIteracoes = int(input('Digite o número de iterações: '))
    # tamanhoPopulacao = int(input('Digite o tamanho da população: '))
    # chance_crossover = float(input('Digite a chance de crossover: '))
    # chance_mutacao = float(input('Digite a chance de mutação: '))

    numTarefas, dicionarioTarefas = ler_arquivo(
        arquivo, numTarefas, dicionarioTarefas)

    # print(json.dumps(dicionarioTarefas, indent=4))

    escreve_ghe(dicionarioTarefas, numProcessadores,
                10, 10, arquivo, numTarefas)

    dic = ler_arquivo_ghe(f'{arquivo[0:-4]}.txt', numProcessadores)

    print(json.dumps(dic, indent=4))

    # populacao = populacaoInicial(
    #     numTarefas, numProcessadores, tamanhoPopulacao, dicionarioTarefas)

    # melhorIndividuo = None

    # for iteracao in range(numeroIteracoes):

    #     if iteracao == 0:
    #         melhorIndividuo = {
    #             'individuo': min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)),
    #             'iteracao': iteracao + 1,
    #             'fitness': fitness(min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)), dicionarioTarefas, numProcessadores, numTarefas)
    #         }

    #     fitnessMedia = sum([fitness(
    #         individuo, dicionarioTarefas, numProcessadores, numTarefas) for individuo in populacao]) / len(populacao)

    #     print(f'Média fitness da população: {fitnessMedia:.7f}')

    #     melhorIndividuoDaPopulacao = {
    #         'individuo': min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)),
    #         'iteracao': iteracao + 1,
    #         'fitness': fitness(min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)), dicionarioTarefas, numProcessadores, numTarefas)
    #     }

    #     if (melhorIndividuoDaPopulacao['fitness'] < melhorIndividuo['fitness']):
    #         melhorIndividuo = melhorIndividuoDaPopulacao

    #     individuosSelecionados = sorted(populacao, key=lambda individuo: fitness(
    #         individuo, dicionarioTarefas, numProcessadores, numTarefas))[:int(tamanhoPopulacao * PORCENTAGEM_SELECAO)]

    #     # selecaoIndividuos(
    #     #     populacao, dicionarioTarefas, numProcessadores, numTarefas, tamanhoPopulacao)

    #     while len(individuosSelecionados) > 1:
    #         pai1 = individuosSelecionados.pop(0)
    #         pai2 = individuosSelecionados.pop(0)

    #         rn = random.random()

    #         if rn < chance_crossover:
    #             filhos = crossover_map(pai1, pai2, numTarefas)
    #             populacao.extend(filhos)
    #         else:
    #             filho = crossover_seq(pai1, pai2, numTarefas)
    #             populacao.append(filho)

    #         mutacao1 = random.random()
    #         mutacao2 = random.random()

    #         if mutacao1 < chance_mutacao:
    #             indice = populacao.index(pai1)
    #             pai1 = mutacao(pai1, numProcessadores)
    #             populacao[indice] = pai1

    #         if mutacao2 < chance_mutacao:
    #             indice = populacao.index(pai2)
    #             pai2 = mutacao(pai2, numProcessadores)
    #             populacao[indice] = pai2

    #     populacao = random.sample(populacao, tamanhoPopulacao)

    # print('Melhor indivíduo:\n')
    # print(f'Iteração: {melhorIndividuo["iteracao"]}')
    # print(f'Fitness: {melhorIndividuo["fitness"]:.7f}')
    # print(f'Individuo: {json.dumps(melhorIndividuo["individuo"], indent=4)}')
    # print(json.dumps(melhorIndividuo, indent=4))
    # print(json.dumps(populacao, indent=4))
