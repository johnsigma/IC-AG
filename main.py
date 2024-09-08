import json
from funcoes import escreve_ghe, ler_arquivo_ghe, ler_numero_tarefas, ler_arquivo, salva_dataframe_em_txt
from MSE import MSE
import numpy as np
import pandas as pd
import time
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

    inicio = time.time()

    grafoRobot = 'grafos_experimento/robot-4-20-30.stg'
    grafoSparse = 'grafos_experimento/sparse-4-100-30.stg'
    grafoFpppp = 'grafos_experimento/fpppp-8-20-30.stg'

    grafos = [grafoRobot, grafoSparse, grafoFpppp]

    parametrosMSE = {
        'tamanhoPopulacao': 20,
        'numeroIteracoes': 2000,
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

        for chave, valor in dicResultadoMSE.items():
            resultados[f'MSE_{chave}'] = {}
            resultados[f'MSE_{chave}']['makespan'] = valor['mediaMakespan']
            resultados[f'MSE_{
                chave}']['loadBalance'] = valor['mediaLoadBalance']
            resultados[f'MSE_{
                chave}']['desvioPadraoMakespan'] = valor['desvioPadraoMakespan']
            resultados[f'MSE_{
                chave}']['desvioPadraoLoadBalance'] = valor['desvioPadraoLoadBalance']

        nomeGrafo = grafo.split('/')[1]

        df = pd.DataFrame.from_dict(resultados, orient='index')

        print(df)

        salva_dataframe_em_txt(df, f'resultados/{nomeGrafo}1.txt')

        fim = time.time()
        tempo_em_segundos = fim - inicio
        tempo_em_minutos = tempo_em_segundos / 60

        with open('resultados/tempo.txt', 'w') as arquivo:
            arquivo.write(f'Tempo de execucao: {tempo_em_minutos} minutos')
