import json
import funcoes
from MSE import MSE
from random import seed

seed(39)

PORCENTAGEM_SELECAO = 0.5


if __name__ == '__main__':
    dicionarioTarefas = {}
    numTarefas = 0

    # arquivo = input('Digite o nome do arquivo: ')
    arquivo = 'exemplo.stg'
    numProcessadores = int(input('Digite o número de processadores: '))
    # numeroIteracoes = int(input('Digite o número de iterações: '))
    # tamanhoPopulacao = int(input('Digite o tamanho da população: '))
    # chance_crossover = float(input('Digite a chance de crossover: '))
    # chance_mutacao = float(input('Digite a chance de mutação: '))

    numTarefas, dicionarioTarefas = funcoes.ler_arquivo(
        arquivo, numTarefas, dicionarioTarefas)

    # print(json.dumps(dicionarioTarefas, indent=4))

    # funcoes.escreve_ghe(dicionarioTarefas, numProcessadores,
    #                     10, 10, arquivo, numTarefas)

    dic = funcoes.ler_arquivo_ghe(f'{arquivo[0:-4]}.txt', numProcessadores)

    print(json.dumps(dic, indent=4))

    mse = MSE(dic, numTarefas, numProcessadores)

    populacao = mse.cria_populacao_inicial(10)

    # print('Pais:\n')
    # print(json.dumps(populacao[0], indent=4))
    # print(json.dumps(populacao[1], indent=4))

    # filhos_alocacao = mse.spx_alocacao(populacao[0], populacao[1])

    # print('Filhos alocação:\n')
    # print(json.dumps(filhos_alocacao[0], indent=4))
    # print(json.dumps(filhos_alocacao[1], indent=4))

    # filhos_escalonamento = mse.spx_escalonamento(populacao[0], populacao[1])

    # print('Filhos escalonamento:\n')
    # print(json.dumps(filhos_escalonamento[0], indent=4))
    # print(json.dumps(filhos_escalonamento[1], indent=4))

    print(populacao[0])

    # print('Mutação escalonamento:\n')
    # mse.stm(populacao[0])
    # print(json.dumps(populacao[0], indent=4))

    print('Mutação alocacao:\n')
    mse.pm(populacao[0])
    print(json.dumps(populacao[0], indent=4))

    # for individuo in populacao:
    #     print(mse.makespan(individuo))

    # print(json.dumps(populacao, indent=4))

    # populacao = populacaoInicial(
    #     numTarefas, numProcessadores, tamanhoPopulacao, dicionarioTarefas)

    # melhorIndividuo = None

    # for iteracao in range(numeroIteracoes):

    #     if iteracao == 0:
    #         melhorIndividuo = {
    #             'individuo': min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)),
    #             'iteracao': iteracao + 1,
    #             'fitness': fitness(min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)), dicionarioTarefas, numProcessadores, numTarefas)
    #         }

    #     fitnessMedia = sum([fitness(
    #         individuo, dicionarioTarefas, numProcessadores, numTarefas) for individuo in populacao]) / len(populacao)

    #     print(f'Média fitness da população: {fitnessMedia:.7f}')

    #     melhorIndividuoDaPopulacao = {
    #         'individuo': min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)),
    #         'iteracao': iteracao + 1,
    #         'fitness': fitness(min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)), dicionarioTarefas, numProcessadores, numTarefas)
    #     }

    #     if (melhorIndividuoDaPopulacao['fitness'] < melhorIndividuo['fitness']):
    #         melhorIndividuo = melhorIndividuoDaPopulacao

    #     individuosSelecionados = sorted(populacao, key=lambda individuo: fitness(
    #         individuo, dicionarioTarefas, numProcessadores, numTarefas))[:int(tamanhoPopulacao * PORCENTAGEM_SELECAO)]

    #     # selecaoIndividuos(
    #     #     populacao, dicionarioTarefas, numProcessadores, numTarefas, tamanhoPopulacao)

    #     while len(individuosSelecionados) > 1:
    #         pai1 = individuosSelecionados.pop(0)
    #         pai2 = individuosSelecionados.pop(0)

    #         rn = random.random()

    #         if rn < chance_crossover:
    #             filhos = crossover_map(pai1, pai2, numTarefas)
    #             populacao.extend(filhos)
    #         else:
    #             filho = crossover_seq(pai1, pai2, numTarefas)
    #             populacao.append(filho)

    #         mutacao1 = random.random()
    #         mutacao2 = random.random()

    #         if mutacao1 < chance_mutacao:
    #             indice = populacao.index(pai1)
    #             pai1 = mutacao(pai1, numProcessadores)
    #             populacao[indice] = pai1

    #         if mutacao2 < chance_mutacao:
    #             indice = populacao.index(pai2)
    #             pai2 = mutacao(pai2, numProcessadores)
    #             populacao[indice] = pai2

    #     populacao = random.sample(populacao, tamanhoPopulacao)

    # print('Melhor indivíduo:\n')
    # print(f'Iteração: {melhorIndividuo["iteracao"]}')
    # print(f'Fitness: {melhorIndividuo["fitness"]:.7f}')
    # print(f'Individuo: {json.dumps(melhorIndividuo["individuo"], indent=4)}')
    # print(json.dumps(melhorIndividuo, indent=4))
    # print(json.dumps(populacao, indent=4))
