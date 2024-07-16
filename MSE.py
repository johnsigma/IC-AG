from random import choice, randint, random
import json


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

        filho1 = []

        filho2 = []

        pontoCorte = randint(0, self.numeroTarefas - 1)

        filho1 = pai1[:pontoCorte] + \
            pai2[pontoCorte:]

        filho2 = pai2[:pontoCorte] + \
            pai1[pontoCorte:]

        return [filho1, filho2]

    def spx_escalonamento(self, pai1, pai2):
        filho1 = []

        filho2 = []

        pontoCorte = randint(0, self.numeroTarefas - 1)

        tarefasFilho1 = pai1[:pontoCorte]
        filho1 = tarefasFilho1

        for tarefa in pai2:
            if tarefa not in tarefasFilho1:
                filho1.append(tarefa)

        tarefasFilho2 = pai2[:pontoCorte]
        filho2 = tarefasFilho2

        for tarefa in pai1:
            if tarefa not in tarefasFilho2:
                filho2.append(tarefa)

        return [filho1, filho2]

    def individuo_valido(self, individuo):
        for tarefa in individuo['escalonamento']:
            predecessores = self.dict[tarefa]['predecessores']

            if not self.predecessores_alocados(individuo['escalonamento'], predecessores):
                print('Individuo inválido')
                return False

        return True

    def stm(self, individuo):
        while True:

            tarefa1 = choice(individuo)
            posicaoTarefa1 = individuo.index(tarefa1)

            while posicaoTarefa1 == 0 or posicaoTarefa1 == len(individuo) - 1:
                tarefa1 = choice(individuo)
                posicaoTarefa1 = individuo.index(tarefa1)

            predecessoresTarefa1 = self.dict[tarefa1]['predecessores']
            limiteInferior = 0

            for tarefa in individuo:
                if len(predecessoresTarefa1) == 0:
                    break
                if tarefa in predecessoresTarefa1:
                    predecessoresTarefa1.remove(tarefa)

                limiteInferior += 1

            novaPosicaoTarefa1 = randint(
                limiteInferior, len(individuo) - 1)

            while novaPosicaoTarefa1 == posicaoTarefa1 or novaPosicaoTarefa1 == 0:
                novaPosicaoTarefa1 = randint(
                    limiteInferior, len(individuo) - 1)

            tarefa2 = individuo[novaPosicaoTarefa1]
            predecessoresTarefa2 = self.dict[tarefa2]['predecessores']

            for i in range(0, posicaoTarefa1):

                tarefa = individuo[i]

                if tarefa in predecessoresTarefa2:
                    predecessoresTarefa2.remove(tarefa)

                if len(predecessoresTarefa2) == 0:
                    novoIndividuo = individuo.copy()
                    novoIndividuo[posicaoTarefa1] = tarefa2
                    novoIndividuo[novaPosicaoTarefa1] = tarefa1
                    # print('Tarefa 1:', tarefa1)
                    # print('Tarefa 2:', tarefa2)
                    # print('Posição tarefa 1:', posicaoTarefa1)
                    # print('Nova posição tarefa 1:', novaPosicaoTarefa1)
                    return novoIndividuo

    def pm(self, individuo):
        posicao = randint(0, len(individuo) - 1)

        while True:
            novoProcessador = randint(0, self.numeroProcessadores - 1)

            if novoProcessador != individuo[posicao]:
                novoIndividuo = individuo.copy()
                novoIndividuo[posicao] = novoProcessador
                return novoIndividuo

    def ajuste_fitness(self, fitness):
        return 1 / fitness

    def soma_fitness(self, fitness):
        return sum(fitness)

    def constroe_roleta(self, populacao, somaFitness):
        roleta = []

        limiteSuperior = 0.0

        for individuo in populacao:
            fitness = self.ajuste_fitness(self.fitness(individuo))
            probabilidade = fitness / somaFitness
            limiteInferior = limiteSuperior
            limiteSuperior = limiteInferior + probabilidade
            roleta.append((limiteInferior, limiteSuperior))

        return roleta

    def selecao_roleta(self, populacao):

        fitness = [self.ajuste_fitness(self.fitness(individuo))
                   for individuo in populacao]

        somaFitness = self.soma_fitness(fitness)

        roleta = self.constroe_roleta(populacao, somaFitness)

        numeroSorteado = random()

        for i, (limiteInferior, limiteSuperior) in enumerate(roleta):
            if limiteInferior <= numeroSorteado < limiteSuperior:
                return i

        print('erro roleta')

        raise ValueError("Não foi possível selecionar um indivíduo da roleta")

    def elitismo(self, populacao, taxaElitismo):
        populacaoOrdenada = sorted(
            populacao, key=lambda individuo: self.fitness(individuo))

        numeroElitismo = int(len(populacao) * taxaElitismo)

        return populacaoOrdenada[:numeroElitismo]

    def inicio(self, tamanhoPopulacao, numeroIteracoes, chanceCrossoverAlocacao, chanceCrossoverEscalonamento, chanceMutacaoAlocacao, chanceMutacaoEscalonamento, taxaElitismo):
        populacao = self.cria_populacao_inicial(tamanhoPopulacao)

        melhorIndividuo = None

        medias = []

        for iteracao in range(numeroIteracoes):

            if iteracao == 0:
                melhorIndividuo = {
                    'individuo': min(populacao, key=lambda individuo: self.fitness(individuo)),
                    'iteracao': iteracao + 1,
                    'fitness': self.fitness(min(populacao, key=lambda individuo: self.fitness(individuo)))
                }

            fitnessMedia = sum([self.fitness(individuo)
                               for individuo in populacao]) / len(populacao)
            medias.append(fitnessMedia)
            print(f'Média fitness da população: {fitnessMedia:.7f}')

            melhorIndividuoDaPopulacao = {
                'individuo': min(populacao, key=lambda individuo: self.fitness(individuo)),
                'iteracao': iteracao + 1,
                'fitness': self.fitness(min(populacao, key=lambda individuo: self.fitness(individuo)))
            }

            if (melhorIndividuoDaPopulacao['fitness'] < melhorIndividuo['fitness']):
                melhorIndividuo = melhorIndividuoDaPopulacao

            elite = self.elitismo(populacao, taxaElitismo)

            novaPopulacao = []

            if iteracao == numeroIteracoes - 1:
                pass

            while len(novaPopulacao) < tamanhoPopulacao - len(elite):

                if iteracao == numeroIteracoes - 1:
                    pass

                pai1 = populacao[self.selecao_roleta(populacao)]

                while pai1 in elite:
                    pai1 = populacao[self.selecao_roleta(populacao)]

                pai2 = populacao[self.selecao_roleta(populacao)]

                while pai2 in elite:
                    pai2 = populacao[self.selecao_roleta(populacao)]

                while pai1 == pai2:
                    pai2 = populacao[self.selecao_roleta(populacao)]

                filhosAlocacao = []
                filhosEscalonamento = []

                if random() < chanceCrossoverAlocacao:
                    filhosAlocacao = self.spx_alocacao(
                        pai1['alocacao'], pai2['alocacao'])
                else:
                    filhosAlocacao = [pai1['alocacao'], pai2['alocacao']]

                if random() < chanceCrossoverEscalonamento:
                    filhosEscalonamento = self.spx_escalonamento(
                        pai1['escalonamento'], pai2['escalonamento'])
                else:
                    filhosEscalonamento = [
                        pai1['escalonamento'], pai2['escalonamento']]

                if random() < chanceMutacaoAlocacao:
                    filhosAlocacao[0] = self.pm(filhosAlocacao[0])
                if random() < chanceMutacaoAlocacao:
                    filhosAlocacao[1] = self.pm(filhosAlocacao[1])

                if random() < chanceMutacaoEscalonamento:
                    filhosEscalonamento[0] = self.stm(filhosEscalonamento[0])
                if random() < chanceMutacaoEscalonamento:
                    filhosEscalonamento[1] = self.stm(filhosEscalonamento[1])

                filho1 = {
                    'alocacao': filhosAlocacao[0],
                    'escalonamento': filhosEscalonamento[0]
                }

                filho2 = {
                    'alocacao': filhosAlocacao[1],
                    'escalonamento': filhosEscalonamento[1]
                }

                if self.individuo_valido(filho1):
                    novaPopulacao.append(filho1)
                if self.individuo_valido(filho2) and len(novaPopulacao) < tamanhoPopulacao - len(elite):
                    novaPopulacao.append(filho2)

            # print(f'Iteração {iteracao + 1} concluída')

            for individuo in elite:
                novaPopulacao.append(individuo)

            populacao = novaPopulacao.copy()

        print('Melhor individuo:')
        print(f'Iteração: {melhorIndividuo["iteracao"]}')
        print(f'Fitness: {melhorIndividuo["fitness"]}')
        print(json.dumps(melhorIndividuo, indent=4))

        return medias

    def load_balance(self, individuo):
        tempoProcessadores = [0] * self.numeroProcessadores

        for indice, tarefa in enumerate(individuo['escalonamento']):
            processador = individuo['alocacao'][indice]
            tempoExecucao = int(
                self.dict[tarefa]['tempos_execucao'][processador])

            tempoProcessadores[processador] += tempoExecucao

        cargaMaxima = max(tempoProcessadores)
        cargaMinima = min(tempoProcessadores)

        return cargaMaxima - cargaMinima

    def fitness(self, individuo, alpha=0.5):
        makespan = self.makespan(individuo)
        loadBalance = self.load_balance(individuo)

        return alpha * makespan + (1 - alpha) * loadBalance
