from random import choice, randint, random


class MSE:
    def __init__(self, dict, numeroTarefas, numeroProcessadores):
        self.dict = dict
        self.numeroTarefas = numeroTarefas
        self.numeroProcessadores = numeroProcessadores

    def cria_cromossomo(self):

        cromossomo = {
            'alocacao': [],
            'escalonamento': []
        }

        listaTarefas = list(self.dict.values())

        while len(cromossomo['escalonamento']) < self.numeroTarefas:

            tarefa = choice(listaTarefas)

            numeroTarefa = tarefa['tarefa']
            predecessores = tarefa['predecessores']

            if numeroTarefa not in cromossomo['escalonamento'] and self.predecessores_alocados(cromossomo['escalonamento'], predecessores):
                cromossomo['escalonamento'].append(numeroTarefa)
                cromossomo['alocacao'].append(
                    choice(range(self.numeroProcessadores)))

        return cromossomo

    def predecessores_alocados(self, cromossomo, predecessores):
        predecessoresAlocados = set(predecessores).issubset(set(cromossomo))

        return predecessoresAlocados

    def cria_populacao_inicial(self, tamanhoPopulacao):

        populacao = []

        for _ in range(tamanhoPopulacao):
            populacao.append(self.cria_cromossomo())

        return populacao

    def makespan(self, cromossomo):
        tempoProcessamento = [0] * self.numeroProcessadores

        for indice, tarefa in enumerate(cromossomo['escalonamento']):
            processador = cromossomo['alocacao'][indice]

            tempoComunicacaoAcc = 0

            predecessores = self.dict[tarefa]['predecessores']

            if len(predecessores) > 0:
                for i, predecessor in enumerate(predecessores):
                    indicePredecessor = cromossomo['escalonamento'].index(
                        predecessor)
                    processadorPredecessor = cromossomo['alocacao'][indicePredecessor]

                    if processadorPredecessor != processador:
                        tempoComunicacao = int(
                            self.dict[tarefa]["custos_comunicacao"][i])
                        # print(f'Comunicacao entre {predecessor} e {tarefa} no processador {
                        #       processadorPredecessor} e {processador} = {tempoComunicacao}')
                        tempoComunicacaoAcc += tempoComunicacao

            tempoProcessamento[processador] += int(self.dict[tarefa]['tempos_execucao'][processador]) + \
                tempoComunicacaoAcc

        return max(tempoProcessamento)

    def spx_alocacao(self, pai1, pai2):

        filho1 = {
            'alocacao': [],
            'escalonamento': pai1['escalonamento']
        }

        filho2 = {
            'alocacao': [],
            'escalonamento': pai2['escalonamento']
        }

        pontoCorte = randint(0, self.numeroTarefas - 1)

        print(f'Ponto de corte: {pontoCorte}')

        filho1['alocacao'] = pai1['alocacao'][:pontoCorte] + \
            pai2['alocacao'][pontoCorte:]

        filho2['alocacao'] = pai2['alocacao'][:pontoCorte] + \
            pai1['alocacao'][pontoCorte:]

        return [filho1, filho2]

    def spx_escalonamento(self, pai1, pai2):
        filho1 = {
            'alocacao': pai1['alocacao'],
            'escalonamento': []
        }

        filho2 = {
            'alocacao': pai2['alocacao'],
            'escalonamento': []
        }

        pontoCorte = randint(0, self.numeroTarefas - 1)

        print(f'Ponto de corte: {pontoCorte}')

        tarefasFilho1 = pai1['escalonamento'][:pontoCorte]
        filho1['escalonamento'] = tarefasFilho1

        for tarefa in pai2['escalonamento']:
            if tarefa not in tarefasFilho1:
                filho1['escalonamento'].append(tarefa)

        tarefasFilho2 = pai2['escalonamento'][:pontoCorte]
        filho2['escalonamento'] = tarefasFilho2

        for tarefa in pai1['escalonamento']:
            if tarefa not in tarefasFilho2:
                filho2['escalonamento'].append(tarefa)

        return [filho1, filho2]

    def individuo_valido(self, individuo):
        for tarefa in individuo['escalonamento']:
            predecessores = self.dict[tarefa]['predecessores']

            if not self.predecessores_alocados(individuo['escalonamento'], predecessores):
                print('Individuo inválido')
                return False

    def stm(self, individuo):
        tarefa1 = choice(individuo['escalonamento'])
        posicaoTarefa1 = individuo['escalonamento'].index(tarefa1)
        predecessoresTarefa1 = self.dict[tarefa1]['predecessores']
        limiteInferior = 0

        for tarefa in individuo['escalonamento']:
            if len(predecessoresTarefa1) == 0:
                break
            if tarefa in predecessoresTarefa1:
                predecessoresTarefa1.remove(tarefa)

            limiteInferior += 1

        print('Limite inferior:', limiteInferior)
        while True:

            novaPosicaoTarefa1 = randint(
                limiteInferior, len(individuo['escalonamento']) - 1)

            tarefa2 = individuo['escalonamento'][novaPosicaoTarefa1]
            predecessoresTarefa2 = self.dict[tarefa2]['predecessores']

            for i in range(0, posicaoTarefa1):

                tarefa = individuo['escalonamento'][i]

                if tarefa in predecessoresTarefa2:
                    predecessoresTarefa2.remove(tarefa)

                if len(predecessoresTarefa2) == 0:
                    individuo['escalonamento'][posicaoTarefa1] = tarefa2
                    individuo['escalonamento'][novaPosicaoTarefa1] = tarefa1
                    # print('Tarefa 1:', tarefa1)
                    # print('Tarefa 2:', tarefa2)
                    # print('Posição tarefa 1:', posicaoTarefa1)
                    # print('Nova posição tarefa 1:', novaPosicaoTarefa1)
                    return

    def pm(self, individuo):
        posicao = randint(0, len(individuo['alocacao']) - 1)

        while True:
            novoProcessador = randint(0, self.numeroProcessadores - 1)

            if novoProcessador != individuo['alocacao'][posicao]:
                print('Posição:', posicao)
                print('Novo processador:', novoProcessador)
                individuo['alocacao'][posicao] = novoProcessador
                return

    def ajuste_fitness(self, fitness):
        return 1 / fitness

    def soma_fitness(self, fitness):
        return sum(fitness)

    def constroe_roleta(self, populacao, somaFitness):
        roleta = []

        limiteSuperior = 0.0

        for individuo in populacao:
            fitness = self.ajuste_fitness(self.makespan(individuo))
            probabilidade = fitness / somaFitness
            limiteInferior = limiteSuperior
            limiteSuperior = limiteInferior + probabilidade
            roleta.append((limiteInferior, limiteSuperior))

        return roleta

    def selecao_roleta(self, populacao):

        fitness = [self.ajuste_fitness(self.makespan(individuo))
                   for individuo in populacao]

        somaFitness = self.soma_fitness(fitness)

        roleta = self.constroe_roleta(populacao, somaFitness)

        numeroSorteado = random()

        for i, (limiteInferior, limiteSuperior) in enumerate(roleta):
            if limiteInferior <= numeroSorteado < limiteSuperior:
                return i

        raise ValueError("Não foi possível selecionar um indivíduo da roleta")
