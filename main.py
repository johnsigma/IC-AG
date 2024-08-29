import json
from funcoes import escreve_ghe, ler_arquivo_ghe, ler_numero_tarefas, ler_arquivo
from MSE import MSE
import numpy as np
from task_scheduling import experimento_breno


def experimento(listaAlphas, arquivoGrafo, parametrosMSE, numProcessadores=None):

    if numProcessadores is None:
        numProcessadores = int(arquivoGrafo.split('-')[1])

    dic = ler_arquivo_ghe(arquivoGrafo, numProcessadores)

    numTarefas = ler_numero_tarefas(arquivoGrafo)

    dicResultado = {}

    for alpha in listaAlphas:

        dicResultado[alpha] = {}

        dicResultado[alpha]['makespan'] = []
        dicResultado[alpha]['loadBalance'] = []

        for i in range(1, 10):

            mse = MSE(dic, numTarefas, numProcessadores, float(alpha))

            mediasFitness, mediasMakespan, mediasLoadBalance, melhorIndividuo = mse.inicio(
                **parametrosMSE)

            dicResultado[alpha]['makespan'].append(melhorIndividuo['makespan'])
            dicResultado[alpha]['loadBalance'].append(
                melhorIndividuo['loadBalance'])

        dicResultado[alpha]['mediaMakespan'] = np.mean(
            dicResultado[alpha]['makespan'])
        dicResultado[alpha]['mediaLoadBalance'] = np.mean(
            dicResultado[alpha]['loadBalance'])
        dicResultado[alpha]['desvioPadraoMakespan'] = np.std(
            dicResultado[alpha]['makespan'])
        dicResultado[alpha]['desvioPadraoLoadBalance'] = np.std(
            dicResultado[alpha]['loadBalance'])

    return dicResultado


if __name__ == '__main__':
    grafoRobot = 'grafos_experimento/robot-4-20-30.stg'
    grafoSparse = 'grafos_experimento/sparse-4-100-30.stg'
    grafoFpppp = 'grafos_experimento/fpppp-8-20-30.stg'

    grafos = [grafoSparse]

    parametrosMSE = {
        'tamanhoPopulacao': 20,
        'numeroIteracoes': 1,
        'chanceCrossoverAlocacao': 0.4,
        'chanceCrossoverEscalonamento': 0.4,
        'chanceMutacaoAlocacao': 0.2,
        'chanceMutacaoEscalonamento': 0.2,
        'taxaElitismo': 0.2
    }

    listaAlphas = ['0', '0.25', '0.5', '0.75', '1']

    for grafo in grafos:
        dicResultadoMSE = experimento(listaAlphas, grafo, parametrosMSE)

        splitGrafo = grafo.split('-')

        numeroTarefas = ler_numero_tarefas(grafo)

        listaProcessadores = [int(splitGrafo[1])]
        variacaoTempoExecucaoLista = [int(splitGrafo[2])]
        variacaoCustoComunicacaoLista = [int(splitGrafo[3].split('.')[0])]
        numTarefasLista = [numeroTarefas]
        diretorioBase = 'grafos_experimento/'

        resultadoBreno = experimento_breno(listaProcessadores, variacaoTempoExecucaoLista,
                                           variacaoCustoComunicacaoLista, numTarefasLista, diretorioBase, 5, True, grafo)

        resultados = {}
        for chave, valor in resultadoBreno.items():
            resultados[chave] = {}
            resultados[chave]['makespan'] = valor[numeroTarefas][grafo]['makespan']
            resultados[chave]['loadBalance'] = valor[numeroTarefas][grafo]['loadBalance']

        # print(json.dumps(resultadoBreno, indent=4))

        resultados['MSE'] = {}

        for chave, valor in dicResultadoMSE.items():
            resultados['MSE']['makespan'] = valor['mediaMakespan']
            resultados['MSE']['loadBalance'] = valor['mediaLoadBalance']
            resultados['MSE']['desvioPadraoMakespan'] = valor['desvioPadraoMakespan']
            resultados['MSE']['desvioPadraoLoadBalance'] = valor['desvioPadraoLoadBalance']

        print(json.dumps(resultados, indent=4))
