import json
import funcoes
from MSE import MSE
from random import seed
from task_scheduling import experimento_breno

PORCENTAGEM_SELECAO = 0.5


def experimento_mse(listaProcessadores, variacaoTempoExecucaoLista, variacaoCustoComunicacaoLista, numTarefasLista, diretorioBase, numeroIteracoes=1000, tamanhoPopulacao=20, chanceCrossoverAlocacao=0.4, chanceCrossoverEscalonamento=0.4, chanceMutacaoAlocacao=0.2, chanceMutacaoEscalonamento=0.2, taxaElitismo=0.3, passo=5):

    # listaProcessadores = [4]
    # variacaoTempoExecucaoLista = [20]
    # variacaoCustoComunicacaoLista = [30]
    # numTarefasLista = [50]
    # diretorioBase = 'grafos_breno/'

    melhoresIndividuos = {
        'MSE': {},
    }

    for numTarefas in numTarefasLista:
        melhoresIndividuos['MSE'][numTarefas] = {}
        i = 0
        dic = 1
        while dic is not None:

            for numProcessadores in listaProcessadores:
                for variacaoTempoExecucao in variacaoTempoExecucaoLista:
                    for variacaoCustoComunicacao in variacaoCustoComunicacaoLista:

                        indiceGrafo = str(i).rjust(3, '0')
                        arquivo = diretorioBase + \
                            f'{numTarefas}/rand0{indiceGrafo}-{numProcessadores}-{
                                variacaoTempoExecucao}-{variacaoCustoComunicacao}.stg'

                        nomeGrafo = f'rand0{
                            indiceGrafo}-{numProcessadores}-{variacaoTempoExecucao}-{variacaoCustoComunicacao}.stg'

                        dic = funcoes.ler_arquivo_ghe(
                            arquivo, numProcessadores)

                        if dic is None:
                            print(f'Arquivo {arquivo} não encontrado')
                            break

                        mse = MSE(dic, numTarefas+2, numProcessadores)

                        mediasFitness, mediasMakespan, mediasLoadBalance, melhorIndividuo = mse.inicio(
                            tamanhoPopulacao, numeroIteracoes, chanceCrossoverAlocacao, chanceCrossoverEscalonamento, chanceMutacaoAlocacao, chanceMutacaoEscalonamento, taxaElitismo)

                        # print('\n----------------------------------------\n')
                        # print(arquivo)
                        # print('Melhor individuo:')
                        # print(f'Iteração: {melhorIndividuo["iteracao"]}')
                        # print(f'Fitness: {melhorIndividuo["fitness"]}')
                        # print(f'Makespan: {melhorIndividuo["makespan"]}')
                        # print(
                        #     f'Load balance: {melhorIndividuo["loadBalance"]}')
                        # print(json.dumps(melhorIndividuo, indent=4))
                        # print('Medias:')
                        mediaFitness = sum(mediasFitness)/len(mediasFitness)
                        # print(
                        #     f'Fitness: {mediaFitness}')
                        mediaMakespan = sum(mediasMakespan)/len(mediasMakespan)
                        # print(
                        #     f'Makespan: {mediaMakespan}')
                        mediaLoadBalance = sum(
                            mediasLoadBalance)/len(mediasLoadBalance)
                        # print(
                        #     f'Load balance: {mediaLoadBalance}')

                        melhoresIndividuos['MSE'][numTarefas][nomeGrafo] = {
                            'makespan': melhorIndividuo['makespan'],
                            'loadBalance': melhorIndividuo['loadBalance'],
                            'fitness': melhorIndividuo['fitness'],
                            'mediaMakespan': mediaMakespan,
                            'mediaLoadBalance': mediaLoadBalance,
                            'mediaFitness': mediaFitness,
                            'iteracao': melhorIndividuo['iteracao']
                        }

            i += passo
    return melhoresIndividuos


if __name__ == '__main__':

    listaProcessadores = [4]
    variacaoTempoExecucaoLista = [20]
    variacaoCustoComunicacaoLista = [30]
    numTarefasLista = [100]
    diretorioBase = 'grafos_breno/'

    iteracoes_mse = 1000
    tamanhoPopulacao_mse = 25
    chanceCrossoverAlocacao_mse = 0.4
    chanceCrossoverEscalonamento_mse = 0.4
    chanceMutacaoAlocacao_mse = 0.2
    chanceMutacaoEscalonamento_mse = 0.2
    taxaElitismo_mse = 0.3

    passo = 3

    melhoresIndividuosMSE = experimento_mse(listaProcessadores, variacaoTempoExecucaoLista, variacaoCustoComunicacaoLista, numTarefasLista, diretorioBase, iteracoes_mse,
                                            tamanhoPopulacao_mse, chanceCrossoverAlocacao_mse, chanceCrossoverEscalonamento_mse, chanceMutacaoAlocacao_mse, chanceMutacaoEscalonamento_mse, taxaElitismo_mse, passo)

    # print('MSE')
    # print(json.dumps(melhoresIndividuosMSE, indent=4))

    resultados_breno = experimento_breno(
        listaProcessadores, variacaoTempoExecucaoLista, variacaoCustoComunicacaoLista, numTarefasLista, diretorioBase, passo)

    # print('Breno')
    # print(json.dumps(resultados_breno, indent=4))

    dicionarioResultados = melhoresIndividuosMSE | resultados_breno

    # funcoes.salva_resultados('resultados.pk1', dicionarioResultados)

    # dicionarioResultados = funcoes.carrega_resultados('resultados.pk1')

    df = funcoes.compare_algorithms(dicionarioResultados)

    funcoes.save_dataframe_to_txt(df, 'resultados/02.txt')
