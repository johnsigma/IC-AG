import json
import funcoes
from MSE import MSE
from random import seed

seed(37)

PORCENTAGEM_SELECAO = 0.5


# if __name__ == '__main__':

#     mediasGrafos = []

#     for i in range(0, 180):

#         dicionarioTarefas = {}
#         numTarefas = 0

#         # arquivo = input('Digite o nome do arquivo: ')
#         strI = str(i)
#         if i < 10:
#             strI = '00' + strI
#         elif i < 100:
#             strI = '0' + strI
#         elif i >= 100:
#             strI = str(i)
#         arquivo = 'grafos/rand0' + strI + '.stg'
#         # numProcessadores = int(input('Digite o número de processadores: '))
#         numProcessadores = 4
#         # numeroIteracoes = int(input('Digite o número de iterações: '))
#         numeroIteracoes = 10
#         # tamanhoPopulacao = int(input('Digite o tamanho da população: '))
#         tamanhoPopulacao = 10
#         # chance_crossover = float(input('Digite a chance de crossover: '))
#         chanceCrossoverAlocacao = 0.4
#         chanceCrossoverEscalonamento = 0.4
#         chanceMutacaoAlocacao = 0.2
#         chanceMutacaoEscalonamento = 0.2
#         taxaElitismo = 0.2
#         # chance_mutacao = float(input('Digite a chance de mutação: '))

#         numTarefas, dicionarioTarefas = funcoes.ler_arquivo(
#             arquivo, numTarefas, dicionarioTarefas)

#         # print(json.dumps(dicionarioTarefas, indent=4))

#         funcoes.escreve_ghe(dicionarioTarefas, numProcessadores,
#                             20, 30, arquivo, numTarefas)

#         dic = funcoes.ler_arquivo_ghe(f'{arquivo[0:-4]}.txt', numProcessadores)

#         # print(json.dumps(dic, indent=4))

#         mse = MSE(dic, numTarefas, numProcessadores)

#         medias = mse.inicio(tamanhoPopulacao, numeroIteracoes, chanceCrossoverAlocacao,
#                             chanceCrossoverEscalonamento, chanceMutacaoAlocacao, chanceMutacaoEscalonamento, taxaElitismo)

#         mediaGrafo = sum(medias)/len(medias)
#         mediasGrafos.append(mediaGrafo)

#         print(f'Media do grafo {arquivo}: {mediaGrafo:.7f}')

#     mediaGeral = sum(mediasGrafos)/len(mediasGrafos)
#     print(f'Media geral: {mediaGeral:.7f}')


if __name__ == '__main__':
    dicionarioTarefas = {}
    numTarefas = 0

    # arquivo = input('Digite o nome do arquivo: ')
    arquivo = 'grafos/robot.stg'
    # numProcessadores = int(input('Digite o número de processadores: '))
    numProcessadores = 4
    # numeroIteracoes = int(input('Digite o número de iterações: '))
    numeroIteracoes = 100
    # tamanhoPopulacao = int(input('Digite o tamanho da população: '))
    tamanhoPopulacao = 30
    # chance_crossover = float(input('Digite a chance de crossover: '))
    chanceCrossoverAlocacao = 0.4
    chanceCrossoverEscalonamento = 0.4
    chanceMutacaoAlocacao = 0.2
    chanceMutacaoEscalonamento = 0.2
    taxaElitismo = 0.4
    # chance_mutacao = float(input('Digite a chance de mutação: '))

    numTarefas, dicionarioTarefas = funcoes.ler_arquivo(
        arquivo, numTarefas, dicionarioTarefas)

    # print(json.dumps(dicionarioTarefas, indent=4))

    # funcoes.escreve_ghe(dicionarioTarefas, numProcessadores,
    #                     20, 30, arquivo, numTarefas)

    dic = funcoes.ler_arquivo_ghe(f'{arquivo[0:-4]}.txt', numProcessadores)

    # print(json.dumps(dic, indent=4))

    mse = MSE(dic, numTarefas, numProcessadores)

    medias = mse.inicio(tamanhoPopulacao, numeroIteracoes, chanceCrossoverAlocacao,
                        chanceCrossoverEscalonamento, chanceMutacaoAlocacao, chanceMutacaoEscalonamento, taxaElitismo)

    mediaGrafo = sum(medias)/len(medias)
    print(f'Media do grafo {arquivo}: {mediaGrafo:.7f}')

    print('pronto')
