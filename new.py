import json
import random

# random.seed(49)

def ler_arquivo(nomeArquivo, numTarefas, dicionarioTarefas):
    with open(nomeArquivo, 'r') as arquivo:
        # Itera sobre cada linha no arquivo
        i = 0
        for linha in arquivo:
            if i == 0:
                numTarefas = int(linha.strip())
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

def geraPrimeiraParteIndividuo(numProcessadores):
    primeiraParteIndividuo = []
    i = 0
    for i in range(numTarefas + 1):
        processador = random.randint(1, numProcessadores)
        primeiraParteIndividuo.append(processador)

    return primeiraParteIndividuo

def geraSegundaParteIndividuo(numTarefas, dicionarioTarefas):
    segundaParteIndividuo = []

    while True:

        if len(segundaParteIndividuo) == numTarefas:
            break

        tarefa = str(random.randint(0, numTarefas + 1))

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
    for i in range(tamanhoPopulacao):
        individuo = {
            'mapeamento': geraPrimeiraParteIndividuo(numProcessadores),
            'sequencia': geraSegundaParteIndividuo(numTarefas, dicionarioTarefas)
        }
        populacao.append(individuo)

    return populacao

def fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas):
    RT = [0] * numProcessadores # RT = Ready Time
    ST = [0] * numTarefas # ST = Start Time
    FT = [0] * numTarefas # FT = Finish Time
    LT = individuo['sequencia'] # LT = List of Tasks
    i = 0
    for i in range(numTarefas):
        tarefa = int(LT.pop(0))
        j = 0
        for j in range(numProcessadores):
            if individuo['mapeamento'][tarefa] == j:
                ST[tarefa] = max(RT[j], FT[tarefa])
                FT[tarefa] = ST[tarefa] + int(dicionarioTarefas[str(tarefa)]['tempo_execucao'])
                RT[j] = FT[tarefa]
            j += 1
        S_length = max(FT)
        i += 1

    return S_length
        
if __name__ == '__main__':
    dicionarioTarefas = {}
    numTarefas = 0

    numTarefas, dicionarioTarefas = ler_arquivo('robot.stg', numTarefas, dicionarioTarefas)

    numProcessadores = 4

    populacao = populacaoInicial(numTarefas, numProcessadores, 50, dicionarioTarefas)

    for individuo in populacao:
        # print(individuo)
        print(fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas))

    # print(json.dumps(populacao, indent=4))