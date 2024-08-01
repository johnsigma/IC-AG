import json
import sys
import funcoes
from MSE import MSE
from random import seed

seed(37)

PORCENTAGEM_SELECAO = 0.5


if __name__ == '__main__':

    mediasGrafos = []

    numProcessadoresList = [4]
    variacaoTempoExecucaoList = [20]
    variacaoCustoComunicacaoList = [30]
    numTarefasList = [50]
    diretorioBase = 'grafos_breno/'

    for numTarefas in numTarefasList:
        for i in range(0, 50, 5):
            for numProcessadores in numProcessadoresList:
                for variacaoTempoExecucao in variacaoTempoExecucaoList:
                    for variacaoCustoComunicacao in variacaoCustoComunicacaoList:
                        dicionarioTarefas = {}

                        indiceGrafo = str(i).rjust(3, '0')
                        arquivo = diretorioBase + \
                            f'{numTarefas}/rand0{indiceGrafo}-{numProcessadores}-{variacaoTempoExecucao}-{variacaoCustoComunicacao}.stg'

                        numeroIteracoes = 1500
                        tamanhoPopulacao = 15
                        chanceCrossoverAlocacao = 0.4
                        chanceCrossoverEscalonamento = 0.4
                        chanceMutacaoAlocacao = 0.3
                        chanceMutacaoEscalonamento = 0.3
                        taxaElitismo = 0.35

                        dic = funcoes.ler_arquivo_ghe(
                            arquivo, numProcessadores)

                        mse = MSE(dic, numTarefas+2, numProcessadores)

                        mediasFitness, mediasMakespan, mediasLoadBalance, melhorIndividuo = mse.inicio(
                            tamanhoPopulacao, numeroIteracoes, chanceCrossoverAlocacao, chanceCrossoverEscalonamento, chanceMutacaoAlocacao, chanceMutacaoEscalonamento, taxaElitismo)
                        print('\n----------------------------------------\n')
                        print(arquivo)
                        print('Melhor individuo:')
                        print(f'Iteração: {melhorIndividuo["iteracao"]}')
                        print(f'Fitness: {melhorIndividuo["fitness"]}')
                        print(f'Makespan: {melhorIndividuo["makespan"]}')
                        print(
                            f'Load balance: {melhorIndividuo["loadBalance"]}')
                        # print(json.dumps(melhorIndividuo, indent=4))
                        print('Medias:')
                        print(
                            f'Fitness: {sum(mediasFitness)/len(mediasFitness)}')
                        print(
                            f'Makespan: {sum(mediasMakespan)/len(mediasMakespan)}')
                        print(
                            f'Load balance: {sum(mediasLoadBalance)/len(mediasLoadBalance)}')


# if __name__ == '__main__':
#     dicionarioTarefas = {}
#     numTarefas = 0

#     # arquivo = input('Digite o nome do arquivo: ')
#     # arquivo = 'grafos/robot.stg'
#     arquivo = 'grafos_breno/rand0000-4-2-30.txt'
#     # numProcessadores = int(input('Digite o número de processadores: '))
#     numProcessadores = 4
#     # numeroIteracoes = int(input('Digite o número de iterações: '))
#     numeroIteracoes = 100
#     # tamanhoPopulacao = int(input('Digite o tamanho da população: '))
#     tamanhoPopulacao = 20
#     # chance_crossover = float(input('Digite a chance de crossover: '))
#     chanceCrossoverAlocacao = 0.4
#     chanceCrossoverEscalonamento = 0.4
#     chanceMutacaoAlocacao = 0.2
#     chanceMutacaoEscalonamento = 0.2
#     taxaElitismo = 0.4
#     # chance_mutacao = float(input('Digite a chance de mutação: '))

#     # numTarefas, dicionarioTarefas = funcoes.ler_arquivo(
#     #     arquivo, numTarefas, dicionarioTarefas)

#     numTarefas = funcoes.ler_numero_tarefas(arquivo)
#     print(numTarefas)

#     # print(json.dumps(dicionarioTarefas, indent=4))

#     # funcoes.escreve_ghe(dicionarioTarefas, numProcessadores,
#     #                     20, 30, arquivo, numTarefas)

#     dic = funcoes.ler_arquivo_ghe(f'{arquivo[0:-4]}.txt', numProcessadores)
#     print(json.dumps(dic, indent=4))

#     sys.exit()

#     mse = MSE(dic, numTarefas, numProcessadores)

#     medias = mse.inicio(tamanhoPopulacao, numeroIteracoes, chanceCrossoverAlocacao,
#                         chanceCrossoverEscalonamento, chanceMutacaoAlocacao, chanceMutacaoEscalonamento, taxaElitismo)

#     mediaGrafo = sum(medias)/len(medias)
#     print(f'Media do grafo {arquivo}: {mediaGrafo:.7f}')

#     print('pronto')
