from random import choice, randint, random, randrange, shuffle, sample
import copy


class MSE:
    def __init__(self, dic, numeroTarefas, numeroProcessadores, alpha=0.5):
        self.dic = dic
        self.numeroTarefas = numeroTarefas
        self.numeroProcessadores = numeroProcessadores
        self.alpha = alpha
        self.taxaElitismo = 0

    def cria_cromossomo(self):

        cromossomo = {"alocacao": [], "escalonamento": []}

        listaTarefas = list(self.dic.values())

        i = 0

        listaNumeroProcessadores = range(self.numeroProcessadores)

        indiceTarefa = None

        tarefa = None

        while len(cromossomo["escalonamento"]) < self.numeroTarefas:

            if i == 0:
                indiceTarefa = 0
                i += 1
            else:
                indiceTarefa = randrange(len(listaTarefas))

            tarefa = listaTarefas[indiceTarefa]

            numeroTarefa = tarefa["tarefa"]
            predecessores = tarefa["predecessores"]

            if numeroTarefa not in cromossomo[
                "escalonamento"
            ] and self.predecessores_alocados(
                cromossomo["escalonamento"], predecessores
            ):
                cromossomo["escalonamento"].append(numeroTarefa)
                cromossomo["alocacao"].append(choice(listaNumeroProcessadores))
                listaTarefas.pop(indiceTarefa)

        cromossomo["makespan"] = self.makespan(cromossomo)
        cromossomo["loadBalance"] = self.load_balance(cromossomo)
        cromossomo["flowtime"] = self.flowtime(cromossomo)
        cromossomo["communicationCost"] = self.communication_cost(cromossomo)
        cromossomo["waitingTime"] = self.waiting_time(cromossomo)
        cromossomo["fitness"] = self.fitness(cromossomo)

        return cromossomo

    def predecessores_alocados(self, escalonamento, predecessores):
        # predecessoresAlocados = set(
        #     predecessores).issubset(set(escalonamento))

        # return predecessoresAlocados

        for predecessor in predecessores:
            if predecessor not in escalonamento:
                return False

        return True

        # return all(predecessor in escalonamento for predecessor in predecessores)

    def cria_populacao_inicial(self, tamanhoPopulacao):
        populacao = [self.cria_cromossomo() for _ in range(tamanhoPopulacao)]

        for individuo in populacao:
            if not self.individuo_valido(individuo):
                print(
                    f"Indivíduo inválido criado na população inicial: {individuo}")
                raise ValueError(
                    "Indivíduo inválido criado na população inicial.")

        return populacao

    def spx_alocacao(self, pai1, pai2):
        try:
            pontoCorte = randint(0, self.numeroTarefas - 1)
            return [
                pai1[:pontoCorte] + pai2[pontoCorte:],
                pai2[:pontoCorte] + pai1[pontoCorte:],
            ]
        except Exception as e:
            print(f"Erro ao realizar SPX na alocação: {e}")

    def spx_escalonamento(self, pai1, pai2):

        try:

            tarefas_reais_pai1 = pai1[1:-1]
            tarefas_reais_pai2 = pai2[1:-1]

            pontoCorte = randint(0, len(tarefas_reais_pai1) - 1)

            tarefasFilho1 = copy.deepcopy(tarefas_reais_pai1[:pontoCorte])
            filho1 = tarefasFilho1

            for tarefa in tarefas_reais_pai2:
                if tarefa not in tarefasFilho1:
                    filho1.append(tarefa)

            tarefasFilho2 = copy.deepcopy(tarefas_reais_pai2[:pontoCorte])
            filho2 = tarefasFilho2

            for tarefa in tarefas_reais_pai1:
                if tarefa not in tarefasFilho2:
                    filho2.append(tarefa)

            filho1 = pai1[0:1] + filho1 + pai1[-1:]
            filho2 = pai2[0:1] + filho2 + pai2[-1:]

            return [filho1, filho2]
        except Exception as e:
            print(f"Erro ao realizar SPX no escalonamento: {e}")

    def individuo_valido(self, individuo):
        try:
            escalonamento = individuo["escalonamento"]

            for indice, tarefa in enumerate(escalonamento):
                predecessores = self.dic[tarefa]["predecessores"]

                # Verifica se todos os predecessores estão presentes no escalonamento
                if not self.predecessores_alocados(escalonamento, predecessores):
                    print(
                        f"Individuo inválido: predecessores da tarefa {tarefa} não estão todos no escalonamento")
                    return False

                # Verifica se cada predecessor aparece antes da tarefa atual no escalonamento
                for predecessor in predecessores:
                    indice_predecessor = escalonamento.index(predecessor)
                    if indice_predecessor >= indice:
                        # print(
                        #     f"Individuo inválido: predecessor {predecessor} da tarefa {tarefa} aparece depois dela no escalonamento")
                        return False

            return True
        except Exception as e:
            print(f"Erro ao validar o indivíduo: {e}")
            return False

    def stm(self, individuo):
        try:
            while True:

                tarefa1 = choice(individuo)
                posicaoTarefa1 = individuo.index(tarefa1)

                while posicaoTarefa1 == 0 or posicaoTarefa1 == len(individuo) - 1:
                    tarefa1 = choice(individuo)
                    posicaoTarefa1 = individuo.index(tarefa1)

                predecessoresTarefa1 = copy.deepcopy(
                    self.dic[tarefa1]["predecessores"])
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
                predecessoresTarefa2 = copy.deepcopy(
                    self.dic[tarefa2]["predecessores"])

                for i in range(0, posicaoTarefa1):

                    tarefa = individuo[i]

                    if tarefa in predecessoresTarefa2:
                        predecessoresTarefa2.remove(tarefa)

                    if len(predecessoresTarefa2) == 0:
                        individuo[posicaoTarefa1] = tarefa2
                        individuo[novaPosicaoTarefa1] = tarefa1
                        # print('Tarefa 1:', tarefa1)
                        # print('Tarefa 2:', tarefa2)
                        # print('Posição tarefa 1:', posicaoTarefa1)
                        # print('Nova posição tarefa 1:', novaPosicaoTarefa1)
                        return individuo

        except Exception as e:
            print(f"Erro ao realizar STM no escalonamento: {e}")

    def pm(self, individuo):
        try:
            posicao = randint(0, len(individuo) - 1)

            while True:
                novoProcessador = randint(0, self.numeroProcessadores - 1)

                if novoProcessador != individuo[posicao]:
                    individuo[posicao] = novoProcessador
                    return individuo

        except Exception as e:
            print(f"Erro ao realizar PM na alocação: {e}")

    def ajuste_fitness(self, fitness):
        if fitness == 0:
            return 1
        return 1 / fitness

    def constroe_roleta(self, populacao, somaFitness):
        roleta = []

        limiteSuperior = 0.0

        for individuo in populacao:
            fitness = self.ajuste_fitness(individuo["fitness"])
            probabilidade = fitness / somaFitness
            limiteInferior = limiteSuperior
            limiteSuperior = limiteInferior + probabilidade
            roleta.append((limiteInferior, limiteSuperior))

        return roleta

    def selecao_roleta(self, populacao):

        fitness = [self.ajuste_fitness(individuo["fitness"])
                   for individuo in populacao]

        somaFitness = sum(fitness)

        roleta = self.constroe_roleta(populacao, somaFitness)

        numeroSorteado = random()

        for i, (limiteInferior, limiteSuperior) in enumerate(roleta):
            if limiteInferior <= numeroSorteado < limiteSuperior:
                return i

        print("erro roleta")

        raise ValueError("Não foi possível selecionar um indivíduo da roleta")

    def elitismo(self, populacao):
        populacaoOrdenada = sorted(populacao, key=lambda x: x["fitness"])

        numeroElitismo = int(len(populacao) * self.taxaElitismo)

        return populacaoOrdenada[:numeroElitismo]

    # Código com a geração de 4 números aleatórios, preservando pais
    def inicio(
        self,
        tamanhoPopulacao,
        numeroIteracoes,
        chanceCrossoverAlocacao,
        chanceCrossoverEscalonamento,
        chanceMutacaoAlocacao,
        chanceMutacaoEscalonamento,
        taxaElitismo
    ):
        populacao = self.cria_populacao_inicial(tamanhoPopulacao)
        self.taxaElitismo = taxaElitismo
        melhorIndividuo = None
        mediasFitness = []
        mediasMakespan = []
        mediasLoadBalance = []

        for iteracao in range(numeroIteracoes):
            individuo = min(populacao, key=lambda x: x["fitness"])

            if iteracao == 0:
                melhorIndividuo = {
                    "individuo": individuo,
                    "iteracao": iteracao + 1,
                    "fitness": individuo["fitness"],
                    "makespan": individuo["makespan"],
                    "loadBalance": individuo["loadBalance"],
                }

            # fitnessMedia = sum([individuo["fitness"] for individuo in populacao]) / len(populacao)
            # mediasFitness.append(fitnessMedia)

            # fitnessMediaMakespan = sum([individuo["makespan"] for individuo in populacao]) / len(populacao)
            # mediasMakespan.append(fitnessMediaMakespan)

            # fitnessMediaLoadBalance = sum([individuo["loadBalance"] for individuo in populacao]) / len(populacao)
            # mediasLoadBalance.append(fitnessMediaLoadBalance)

            melhorIndividuoDaPopulacao = {
                "individuo": individuo,
                "iteracao": iteracao + 1,
                "fitness": individuo["fitness"],
                "makespan": individuo["makespan"],
                "loadBalance": individuo["loadBalance"],
                "flowtime": individuo["flowtime"],
                "communicationCost": individuo["communicationCost"],
                "waitingTime": individuo["waitingTime"],
            }

            if melhorIndividuoDaPopulacao["fitness"] < melhorIndividuo["fitness"]:
                melhorIndividuo = copy.deepcopy(melhorIndividuoDaPopulacao)

            elite = self.elitismo(populacao)

            novaPopulacao = []

            while len(novaPopulacao) < tamanhoPopulacao - len(elite):

                pai1_original = populacao[self.selecao_roleta(populacao)]
                pai2_original = populacao[self.selecao_roleta(populacao)]

                while pai1_original == pai2_original:
                    pai2_original = populacao[self.selecao_roleta(populacao)]

                pai1 = copy.deepcopy(pai1_original)
                pai2 = copy.deepcopy(pai2_original)

                filhosAlocacao = []
                filhosEscalonamento = []

                if random() < chanceCrossoverAlocacao:
                    filhosAlocacao = self.spx_alocacao(
                        pai1["alocacao"], pai2["alocacao"]
                    )
                else:
                    filhosAlocacao = [pai1["alocacao"], pai2["alocacao"]]

                if random() < chanceCrossoverEscalonamento:
                    filhosEscalonamento = self.spx_escalonamento(
                        pai1["escalonamento"], pai2["escalonamento"]
                    )
                else:
                    filhosEscalonamento = [
                        pai1["escalonamento"], pai2["escalonamento"]]

                if random() < chanceMutacaoAlocacao:
                    filhosAlocacao[0] = self.pm(filhosAlocacao[0])
                if random() < chanceMutacaoAlocacao:
                    filhosAlocacao[1] = self.pm(filhosAlocacao[1])

                if random() < chanceMutacaoEscalonamento:
                    filhosEscalonamento[0] = self.stm(filhosEscalonamento[0])
                if random() < chanceMutacaoEscalonamento:
                    filhosEscalonamento[1] = self.stm(filhosEscalonamento[1])

                filho1 = {
                    "alocacao": filhosAlocacao[0],
                    "escalonamento": filhosEscalonamento[0],
                }
                # Calcula métricas antes do fitness
                filho1["makespan"] = self.makespan(filho1)
                filho1["loadBalance"] = self.load_balance(filho1)
                filho1["flowtime"] = self.flowtime(filho1)
                filho1["communicationCost"] = self.communication_cost(filho1)
                filho1["waitingTime"] = self.waiting_time(filho1)
                filho1["fitness"] = self.fitness(filho1)
                filho2 = {
                    "alocacao": filhosAlocacao[1],
                    "escalonamento": filhosEscalonamento[1],
                }
                filho2["makespan"] = self.makespan(filho2)
                filho2["loadBalance"] = self.load_balance(filho2)
                filho2["flowtime"] = self.flowtime(filho2)
                filho2["communicationCost"] = self.communication_cost(filho2)
                filho2["waitingTime"] = self.waiting_time(filho2)
                filho2["fitness"] = self.fitness(filho2)

                if self.individuo_valido(filho1):
                    novaPopulacao.append(filho1)
                if self.individuo_valido(filho2) and len(
                    novaPopulacao
                ) < tamanhoPopulacao - len(elite):
                    novaPopulacao.append(filho2)

            # print(f'Iteração {iteracao + 1} concluída')

            novaPopulacao.extend(elite)

            shuffle(novaPopulacao)

            populacao = novaPopulacao.copy()

        return mediasFitness, mediasMakespan, mediasLoadBalance, melhorIndividuo

    # Código com a geração de 2 números aleatórios, sempre gerando filhos diferentes dos pais

    # def inicio(self, tamanhoPopulacao, numeroIteracoes, chanceCrossover, chanceMutacao, taxaElitismo):

    #     populacao = self.cria_populacao_inicial(tamanhoPopulacao)

    #     melhorIndividuo = None

    #     mediasFitness = []
    #     mediasMakespan = []
    #     mediasLoadBalance = []

    #     for iteracao in range(numeroIteracoes):

    #         if iteracao == 0:
    #             individuo = min(
    #                 populacao, key=lambda individuo: self.fitness(individuo))
    #             melhorIndividuo = {
    #                 'individuo': individuo,
    #                 'iteracao': iteracao + 1,
    #                 'fitness': self.fitness(individuo),
    #                 'makespan': self.makespan(individuo),
    #                 'loadBalance': self.load_balance(individuo)
    #             }

    #         fitnessMedia = sum([self.fitness(individuo)
    #                            for individuo in populacao]) / len(populacao)
    #         mediasFitness.append(fitnessMedia)
    #         # print(f'\nMédia fitness da população: {fitnessMedia:.7f}')

    #         fitnessMediaMakespan = sum([self.makespan(individuo)
    #                                     for individuo in populacao]) / len(populacao)
    #         mediasMakespan.append(fitnessMediaMakespan)
    #         # print(f'\nMédia makespan da população: {fitnessMediaMakespan:.7f}')

    #         fitnessMediaLoadBalance = sum([self.load_balance(individuo)
    #                                        for individuo in populacao]) / len(populacao)
    #         mediasLoadBalance.append(fitnessMediaLoadBalance)
    #         # print(f'\nMédia loadbalance da população: {fitnessMediaLoadBalance:.7f}')

    #         individuo = min(
    #             populacao, key=lambda individuo: self.fitness(individuo))

    #         melhorIndividuoDaPopulacao = {
    #             'individuo': individuo,
    #             'iteracao': iteracao + 1,
    #             'fitness': self.fitness(individuo),
    #             'makespan': self.makespan(individuo),
    #             'loadBalance': self.load_balance(individuo)
    #         }

    #         if (melhorIndividuoDaPopulacao['fitness'] < melhorIndividuo['fitness']):
    #             melhorIndividuo = melhorIndividuoDaPopulacao

    #         elite = self.elitismo(populacao, taxaElitismo)

    #         novaPopulacao = []

    #         if iteracao == numeroIteracoes - 1:
    #             pass

    #         while len(novaPopulacao) < tamanhoPopulacao - len(elite):

    #             if iteracao == numeroIteracoes - 1:
    #                 pass

    #             pai1 = populacao[self.selecao_roleta(populacao)]

    #             while pai1 in elite:
    #                 pai1 = populacao[self.selecao_roleta(populacao)]

    #             pai2 = populacao[self.selecao_roleta(populacao)]

    #             while pai2 in elite:
    #                 pai2 = populacao[self.selecao_roleta(populacao)]

    #             while pai1 == pai2:
    #                 pai2 = populacao[self.selecao_roleta(populacao)]

    #             filhosAlocacao = [pai1['alocacao'], pai2['alocacao']]
    #             filhosEscalonamento = [
    #                 pai1['escalonamento'], pai2['escalonamento']]

    #             if random() < chanceCrossover:
    #                 filhosAlocacao = self.spx_alocacao(
    #                     filhosAlocacao[0], filhosAlocacao[1])
    #             else:
    #                 filhosEscalonamento = self.spx_escalonamento(
    #                     filhosEscalonamento[0], filhosEscalonamento[1])

    #             if random() < chanceMutacao:
    #                 filhosAlocacao[0] = self.pm(filhosAlocacao[0])
    #                 filhosAlocacao[1] = self.pm(filhosAlocacao[1])
    #             else:
    #                 filhosEscalonamento[0] = self.stm(filhosEscalonamento[0])
    #                 filhosEscalonamento[1] = self.stm(filhosEscalonamento[1])

    #             filho1 = {
    #                 'alocacao': filhosAlocacao[0],
    #                 'escalonamento': filhosEscalonamento[0]
    #             }

    #             filho2 = {
    #                 'alocacao': filhosAlocacao[1],
    #                 'escalonamento': filhosEscalonamento[1]
    #             }

    #             if self.individuo_valido(filho1):
    #                 novaPopulacao.append(filho1)
    #             if self.individuo_valido(filho2) and len(novaPopulacao) < tamanhoPopulacao - len(elite):
    #                 novaPopulacao.append(filho2)

    #         # print(f'Iteração {iteracao + 1} concluída')

    #         for individuo in elite:
    #             novaPopulacao.append(individuo)

    #         populacao = novaPopulacao.copy()

    #     return mediasFitness, mediasMakespan, mediasLoadBalance, melhorIndividuo

    # Load balance "antigo"
    # def load_balance(self, individuo):
    #     tempoProcessadores = [0] * self.numeroProcessadores

    #     for indice, tarefa in enumerate(individuo['escalonamento']):
    #         processador = individuo['alocacao'][indice]
    #         tempoExecucao = int(
    #             self.dic[tarefa]['tempos_execucao'][processador])

    #         tempoProcessadores[processador] += tempoExecucao

    #     cargaMaxima = max(tempoProcessadores)
    #     cargaMinima = min(tempoProcessadores)

    #     return cargaMaxima - cargaMinima

    def makespan(self, cromossomo):
        tempoProcessamento = [0] * self.numeroProcessadores

        for indice, tarefa in enumerate(cromossomo["escalonamento"]):
            processador = cromossomo["alocacao"][indice]

            tempoComunicacaoAcc = 0

            predecessores = self.dic[tarefa]["predecessores"]

            if len(predecessores) > 0:
                for i, predecessor in enumerate(predecessores):
                    indicePredecessor = cromossomo["escalonamento"].index(
                        predecessor)
                    processadorPredecessor = cromossomo["alocacao"][indicePredecessor]

                    if processadorPredecessor != processador:
                        tempoComunicacao = int(
                            self.dic[tarefa]["custos_comunicacao"][i]
                        )
                        # print(f'Comunicacao entre {predecessor} e {tarefa} no processador {
                        #       processadorPredecessor} e {processador} = {tempoComunicacao}')
                        tempoComunicacaoAcc += tempoComunicacao

            tempoProcessamento[processador] += (
                int(self.dic[tarefa]["tempos_execucao"][processador])
                + tempoComunicacaoAcc
            )

        return max(tempoProcessamento)

    # Load balance "novo", inspirado no trabalho do Breno

    def load_balance(self, individuo):
        tempoProcessadores = [0] * self.numeroProcessadores

        for indice, tarefa in enumerate(individuo["escalonamento"]):
            processador = individuo["alocacao"][indice]
            tempoExecucao = int(
                self.dic[tarefa]["tempos_execucao"][processador])

            tempoProcessadores[processador] += tempoExecucao

        tempoProcessamentoTotal = sum(tempoProcessadores)

        tempoMedioProcessamento = tempoProcessamentoTotal / self.numeroProcessadores

        makespan = individuo["makespan"]

        return makespan / tempoMedioProcessamento

    def flowtime(self, cromossomo):
        finish_times = [0] * self.numeroTarefas

        for indice, tarefa in enumerate(cromossomo["escalonamento"]):
            processador = cromossomo["alocacao"][indice]
            tempoExecucao = int(
                self.dic[tarefa]["tempos_execucao"][processador])

            # Calculate communication delay
            tempoComunicacaoAcc = 0
            predecessores = self.dic[tarefa]["predecessores"]

            for i, predecessor in enumerate(predecessores):
                indicePredecessor = cromossomo["escalonamento"].index(
                    predecessor)
                processadorPredecessor = cromossomo["alocacao"][indicePredecessor]

                if processadorPredecessor != processador:
                    tempoComunicacao = int(
                        self.dic[tarefa]["custos_comunicacao"][i])
                    tempoComunicacaoAcc = max(
                        tempoComunicacaoAcc,
                        finish_times[indicePredecessor] + tempoComunicacao,
                    )
                else:
                    tempoComunicacaoAcc = max(
                        tempoComunicacaoAcc, finish_times[indicePredecessor])

            finish_times[indice] = tempoExecucao + tempoComunicacaoAcc

        return sum(finish_times)

    def communication_cost(self, cromossomo):
        total_communication_cost = 0

        for indice, tarefa in enumerate(cromossomo["escalonamento"]):
            processador = cromossomo["alocacao"][indice]
            predecessores = self.dic[tarefa]["predecessores"]

            for i, predecessor in enumerate(predecessores):
                indicePredecessor = cromossomo["escalonamento"].index(
                    predecessor)
                processadorPredecessor = cromossomo["alocacao"][indicePredecessor]

                if processadorPredecessor != processador:
                    total_communication_cost += int(
                        self.dic[tarefa]["custos_comunicacao"][i])

        return total_communication_cost

    def waiting_time(self, individuo):
        tempoEsperaTotal = 0
        # Armazena o tempo de finalização de cada tarefa.
        temposFinalizacao = [0] * self.numeroTarefas

        for indice, tarefa in enumerate(individuo["escalonamento"]):
            processador = individuo["alocacao"][indice]
            predecessores = self.dic[tarefa]["predecessores"]
            tempoInicio = 0

            # Calcula o maior tempo de término dos predecessores
            for i, predecessor in enumerate(predecessores):
                indicePredecessor = individuo["escalonamento"].index(
                    predecessor)
                processadorPredecessor = individuo["alocacao"][indicePredecessor]
                tempoFinalizacaoPredecessor = temposFinalizacao[indicePredecessor]

                # Inclui o custo de comunicação se os processadores forem diferentes
                if processadorPredecessor != processador:
                    tempoFinalizacaoPredecessor += int(
                        self.dic[tarefa]["custos_comunicacao"][i]
                    )

                tempoInicio = max(tempoInicio, tempoFinalizacaoPredecessor)

            # Calcula o tempo de finalização da tarefa
            tempoExecucao = int(
                self.dic[tarefa]["tempos_execucao"][processador])
            temposFinalizacao[indice] = tempoInicio + tempoExecucao

            # O tempo de espera da tarefa é o tempo de início menos o tempo de término do último predecessor
            tempoEspera = tempoInicio - max(
                [temposFinalizacao[individuo["escalonamento"].index(
                    pred)] for pred in predecessores],
                default=0
            )
            tempoEsperaTotal += max(0, tempoEspera)

        return tempoEsperaTotal

    def fitness(self, individuo):
        makespan = individuo["makespan"]
        loadBalance = individuo["loadBalance"]
        flowtime = individuo["flowtime"]
        waitingTime = individuo["waitingTime"]
        communicationCost = individuo["communicationCost"]

        return self.alpha * makespan + (1 - self.alpha) * loadBalance

        # return self.alpha * makespan + (1 - self.alpha) * communicationCost

    # def ag(self, populacao, novaPopulacao, chanceCrossoverAlocacao, chanceCrossoverEscalonamento, chanceMutacaoAlocacao, chanceMutacaoEscalonamento, tamanhoPopulacao, elite):
    #     pai1 = populacao[self.selecao_roleta(populacao)]
    #     pai2 = populacao[self.selecao_roleta(populacao)]

    #     while pai1 == pai2:
    #         pai2 = populacao[self.selecao_roleta(populacao)]

    #     filhosAlocacao = []
    #     filhosEscalonamento = []

    #     if random() < chanceCrossoverAlocacao:
    #         filhosAlocacao = self.spx_alocacao(
    #             pai1["alocacao"], pai2["alocacao"]
    #         )
    #     else:
    #         filhosAlocacao = [pai1["alocacao"], pai2["alocacao"]]

    #     if random() < chanceCrossoverEscalonamento:
    #         filhosEscalonamento = self.spx_escalonamento(
    #             pai1["escalonamento"], pai2["escalonamento"]
    #         )
    #     else:
    #         filhosEscalonamento = [
    #             pai1["escalonamento"], pai2["escalonamento"]]

    #     if random() < chanceMutacaoAlocacao:
    #         filhosAlocacao[0] = self.pm(filhosAlocacao[0])
    #     if random() < chanceMutacaoAlocacao:
    #         filhosAlocacao[1] = self.pm(filhosAlocacao[1])

    #     if random() < chanceMutacaoEscalonamento:
    #         filhosEscalonamento[0] = self.stm(filhosEscalonamento[0])
    #     if random() < chanceMutacaoEscalonamento:
    #         filhosEscalonamento[1] = self.stm(filhosEscalonamento[1])

    #     filho1 = {
    #         "alocacao": filhosAlocacao[0],
    #         "escalonamento": filhosEscalonamento[0],
    #     }
    #     filho1["makespan"] = self.makespan(filho1)
    #     filho1["loadBalance"] = self.load_balance(filho1)
    #     filho1["fitness"] = self.fitness(filho1)
    #     filho1["flowtime"] = self.flowtime(filho1)
    #     filho1["communicationCost"] = self.communication_cost(filho1)
    #     filho1["waitingTime"] = self.waiting_time(filho1)
    #     filho2 = {
    #         "alocacao": filhosAlocacao[1],
    #         "escalonamento": filhosEscalonamento[1],
    #     }
    #     filho2["makespan"] = self.makespan(filho2)
    #     filho2["loadBalance"] = self.load_balance(filho2)
    #     filho2["fitness"] = self.fitness(filho2)
    #     filho2["flowtime"] = self.flowtime(filho2)
    #     filho2["communicationCost"] = self.communication_cost(filho2)
    #     filho2["waitingTime"] = self.waiting_time(filho2)

    #     if self.individuo_valido(filho1):
    #         novaPopulacao.append(filho1)

    #     if self.individuo_valido(filho2) and len(
    #         novaPopulacao
    #     ) < tamanhoPopulacao - len(elite):
    #         novaPopulacao.append(filho2)

    #     return novaPopulacao

    # Experimento com evolução da população e todas as métricas

    def experimento_evolucao_populacao(self, numeroIteracoes, chanceCrossoverAlocacao, chanceCrossoverEscalonamento, chanceMutacaoAlocacao, chanceMutacaoEscalonamento, taxaElitismo, populacao, tamanhoPopulacao):
        try:
            self.taxaElitismo = taxaElitismo

            # --- CORREÇÃO: Salva uma cópia profunda da população inicial ANTES de qualquer iteração ---
            individuosPrimeiraIteracao = copy.deepcopy(populacao)

            mediasFitness = []
            mediasMakespan = []
            mediasLoadBalance = []
            mediasFlowtime = []
            mediasCommunicationCost = []
            mediasWaitingTime = []
            # A linha abaixo foi movida para cima e agora usa deepcopy
            # individuosPrimeiraIteracao = []

            for iteracao in range(numeroIteracoes):

                somaFitness = 0
                somaMakespan = 0
                somaLoadBalance = 0
                somaFlowtime = 0
                somaCommunicationCost = 0
                somaWaitingTime = 0

                # O bloco que salvava a primeira iteração aqui dentro foi removido, pois já foi feito.
                for individuo in populacao:
                    somaFitness += individuo["fitness"]
                    somaMakespan += individuo["makespan"]
                    somaLoadBalance += individuo["loadBalance"]
                    somaFlowtime += individuo["flowtime"]
                    somaCommunicationCost += individuo["communicationCost"]
                    somaWaitingTime += individuo["waitingTime"]

                fitnessMedia = somaFitness / tamanhoPopulacao
                mediasFitness.append(fitnessMedia)

                makespanMedia = somaMakespan / tamanhoPopulacao
                mediasMakespan.append(makespanMedia)

                loadBalanceMedia = somaLoadBalance / tamanhoPopulacao
                mediasLoadBalance.append(loadBalanceMedia)

                flowtimeMedia = somaFlowtime / tamanhoPopulacao
                mediasFlowtime.append(flowtimeMedia)

                communicationCostMedia = somaCommunicationCost / tamanhoPopulacao
                mediasCommunicationCost.append(communicationCostMedia)

                waitingTimeMedia = somaWaitingTime / tamanhoPopulacao
                mediasWaitingTime.append(waitingTimeMedia)

                elite = self.elitismo(populacao)
                novaPopulacao = []

                while len(novaPopulacao) < tamanhoPopulacao - len(elite):
                    pai1_original = populacao[self.selecao_roleta(populacao)]
                    pai2_original = populacao[self.selecao_roleta(populacao)]

                    while pai1_original == pai2_original:
                        pai2_original = populacao[self.selecao_roleta(
                            populacao)]

                    # --- CORREÇÃO: Cópia profunda para isolar os pais do resto da população ---
                    pai1 = copy.deepcopy(pai1_original)
                    pai2 = copy.deepcopy(pai2_original)

                    filhosAlocacao = []
                    filhosEscalonamento = []

                    if random() < chanceCrossoverAlocacao:
                        filhosAlocacao = self.spx_alocacao(
                            pai1["alocacao"], pai2["alocacao"]
                        )
                    else:
                        filhosAlocacao = [pai1["alocacao"], pai2["alocacao"]]

                    if random() < chanceCrossoverEscalonamento:
                        filhosEscalonamento = self.spx_escalonamento(
                            pai1["escalonamento"], pai2["escalonamento"]
                        )
                    else:
                        filhosEscalonamento = [
                            pai1["escalonamento"], pai2["escalonamento"]]

                    if random() < chanceMutacaoAlocacao:
                        filhosAlocacao[0] = self.pm(filhosAlocacao[0])
                    if random() < chanceMutacaoAlocacao:
                        filhosAlocacao[1] = self.pm(filhosAlocacao[1])

                    if random() < chanceMutacaoEscalonamento:
                        filhosEscalonamento[0] = self.stm(
                            filhosEscalonamento[0])
                    if random() < chanceMutacaoEscalonamento:
                        filhosEscalonamento[1] = self.stm(
                            filhosEscalonamento[1])

                    filho1 = {
                        "alocacao": filhosAlocacao[0],
                        "escalonamento": filhosEscalonamento[0],
                    }
                    filho1["makespan"] = self.makespan(filho1)
                    filho1["loadBalance"] = self.load_balance(filho1)
                    filho1["flowtime"] = self.flowtime(filho1)
                    filho1["communicationCost"] = self.communication_cost(
                        filho1)
                    filho1["waitingTime"] = self.waiting_time(filho1)
                    filho1["fitness"] = self.fitness(filho1)
                    filho2 = {
                        "alocacao": filhosAlocacao[1],
                        "escalonamento": filhosEscalonamento[1],
                    }
                    filho2["makespan"] = self.makespan(filho2)
                    filho2["loadBalance"] = self.load_balance(filho2)
                    filho2["flowtime"] = self.flowtime(filho2)
                    filho2["communicationCost"] = self.communication_cost(
                        filho2)
                    filho2["waitingTime"] = self.waiting_time(filho2)
                    filho2["fitness"] = self.fitness(filho2)

                    if self.individuo_valido(filho1):
                        novaPopulacao.append(filho1)

                    if self.individuo_valido(filho2) and len(
                        novaPopulacao
                    ) < tamanhoPopulacao - len(elite):
                        novaPopulacao.append(filho2)

                for individuo in novaPopulacao:
                    if self.individuo_valido(individuo) == False:
                        print(
                            f"Indivíduo inválido encontrado na nova população: {individuo}")

                novaPopulacao.extend(elite)
                shuffle(novaPopulacao)
                populacao = novaPopulacao.copy()

            individuosUltimaIteracao = []

            for individuo in populacao:
                individuosUltimaIteracao.append({
                    "makespan": individuo["makespan"],
                    "loadBalance": individuo["loadBalance"],
                    "flowtime": individuo["flowtime"],
                    "communicationCost": individuo["communicationCost"],
                    "waitingTime": individuo["waitingTime"],
                    "fitness": individuo["fitness"],
                    "alocacao": individuo["alocacao"],
                    "escalonamento": individuo["escalonamento"]
                })

            return {
                "primeiraIteracao": individuosPrimeiraIteracao,
                "ultimaIteracao": individuosUltimaIteracao,
                "mediasFitness": mediasFitness,
                "mediasMakespan": mediasMakespan,
                "mediasLoadBalance": mediasLoadBalance,
                "mediasFlowtime": mediasFlowtime,
                "mediasCommunicationCost": mediasCommunicationCost,
                "mediasWaitingTime": mediasWaitingTime
            }
        except Exception as e:
            print(f"Erro no experimento de evolução da população: {e}")
            return None

# Implementei + 3 funcoes
    # flowtime
    # communication cost
    # waiting time

    # Experimento:
    # Gerar uma populacão de 1000 indivíduos
    # Avaliar cada um deles em relacao a cada função objetivo
    # Uma tabela com esses valores para cada indivíduo
    # Salvar os indivíduos
    # (+) Repetir essa avaliação na população final

    # Objetivo: cada função - quão discriminatória ela é?

    # Outro experimento: combinar as funções objetivo duas a duas.
