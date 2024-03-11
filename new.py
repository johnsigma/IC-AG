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


def selecaoIndividuos(populacao, dicionarioTarefas, numProcessadores, numTarefas):
    individuosSelecionados = []
    individuosSorteados = []

    while True:
        if len(individuosSelecionados) == int(len(populacao) * PORCENTAGEM_SELECAO):
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

        # print(individuo1)
        # print(individuo2)

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


if __name__ == '__main__':
    dicionarioTarefas = {}
    numTarefas = 0

    numTarefas, dicionarioTarefas = ler_arquivo(
        'robot.stg', numTarefas, dicionarioTarefas)

    numProcessadores = 4
    numeroIteracoes = 100
    tamanhoPopulacao = 50

    populacao = populacaoInicial(
        numTarefas, numProcessadores, tamanhoPopulacao, dicionarioTarefas)

    for iteracao in range(numeroIteracoes):
        individuosSelecionados = selecaoIndividuos(
            populacao, dicionarioTarefas, numProcessadores, numTarefas)

        for individuo in individuosSelecionados:
            print(fitness(individuo, dicionarioTarefas,
                  numProcessadores, numTarefas))

    # for individuo in populacao:
    #     # print(individuo)
    #     print(fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas))

    # print(json.dumps(populacao, indent=4))
