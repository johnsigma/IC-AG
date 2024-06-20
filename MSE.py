from random import choice


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

        while len(cromossomo['alocacao']) < self.numeroTarefas:

            tarefa = choice(listaTarefas)

            numeroTarefa = tarefa['tarefa']
            predecessores = tarefa['predecessores']

            if numeroTarefa not in cromossomo['alocacao'] and self.predecessores_alocados(cromossomo['alocacao'], predecessores):
                cromossomo['alocacao'].append(numeroTarefa)
                cromossomo['escalonamento'].append(
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

        for indice, tarefa in enumerate(cromossomo['alocacao']):
            processador = cromossomo['escalonamento'][indice]

            tempoComunicacaoAcc = 0

            predecessores = self.dict[tarefa]['predecessores']

            if len(predecessores) > 0:
                for i, predecessor in enumerate(predecessores):
                    indicePredecessor = cromossomo['alocacao'].index(
                        predecessor)
                    processadorPredecessor = cromossomo['escalonamento'][indicePredecessor]

                    if processadorPredecessor != processador:
                        tempoComunicacao = int(
                            self.dict[tarefa]["custos_comunicacao"][i])
                        # print(f'Comunicacao entre {predecessor} e {tarefa} no processador {
                        #       processadorPredecessor} e {processador} = {tempoComunicacao}')
                        tempoComunicacaoAcc += tempoComunicacao

            tempoProcessamento[processador] += int(self.dict[tarefa]['tempos_execucao'][processador]) + \
                tempoComunicacaoAcc

        return max(tempoProcessamento)
