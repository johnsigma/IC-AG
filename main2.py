import os
import random
from sys import argv
from time import time
from uuid import uuid4
import pandas as pd
import numpy as np
from funcoes import (
    ler_arquivo_ghe,
    ler_numero_tarefas,
    gera_populacao_inicial,
    salva_populacao,
    carrega_populacao,
    gera_hash,
)
from MSE import MSE
from tkinter import Tk


# seed = 42
# np.random.seed(seed)
# random.seed(seed)


def salva(parametros):

    try:

        tamanhoPopulacao = parametros["tamanhoPopulacao"]
        grafo = parametros["grafo"]

        numTarefas = ler_numero_tarefas(grafo)
        numProcessadores = int(grafo.split("-")[1])
        dic = ler_arquivo_ghe(grafo, numProcessadores)
        populacao = gera_populacao_inicial(
            dic, numTarefas, numProcessadores, tamanhoPopulacao
        )
        hashPopulacao = salva_populacao(populacao)
        return hashPopulacao
    except:
        print("Erro ao salvar")
        return False


def carrega(hashPopulacao):
    try:
        populacao = carrega_populacao(hashPopulacao)
        return populacao
    except:
        print("Erro ao carregar")
        return False


def experimento(
    listaAlphas,
    dic,
    parametrosMSE,
    numTarefas,
    populacao,
    hashPopulacao,
    numProcessadores=None,
):
    resultados = {}

    for alpha in listaAlphas:
        resultados["alpha"] = {}
        resultados["alpha"]["makespan"] = []
        resultados["alpha"]["loadBalance"] = []
        resultados["alpha"]["iteracao"] = []
        resultados["alpha"]["flowtime"] = []
        resultados["alpha"]["communicationCost"] = []
        resultados["alpha"]["waitingTime"] = []

        mse = MSE(dic, numTarefas, numProcessadores, float(alpha))

        resultadosExperimento = mse.experimento_evolucao_populacao(
            parametrosMSE["numeroIteracoes"],
            parametrosMSE["chanceCrossoverAlocacao"],
            parametrosMSE["chanceCrossoverEscalonamento"],
            parametrosMSE["chanceMutacaoAlocacao"],
            parametrosMSE["chanceMutacaoEscalonamento"],
            parametrosMSE["taxaElitismo"],
            populacao,
            parametrosMSE["tamanhoPopulacao"],
        )

        parametrosMSE["alpha"] = alpha

        salva_resultados(
            resultadosExperimento["primeiraIteracao"],
            resultadosExperimento["ultimaIteracao"],
            parametrosMSE,
            hashPopulacao,
            alpha,
        )


def salva_resultados(
    individuosPrimeiraIteracao,
    individuosUltimaIteracao,
    parametrosMSE,
    hashPopulacao,
    alpha,
):
    try:

        pastaResultados = "resultados2"

        dicPrimeiraIteracao = {}
        dicUltimaIteracao = {}
        # dicEscalonamento = {}

        for i, _ in enumerate(individuosUltimaIteracao):
            individuoPrimeiraIteracao = individuosPrimeiraIteracao[i]
            individuoUltimaIteracao = individuosUltimaIteracao[i]

            dicPrimeiraIteracao[str(i)] = {
                "Individuo": str(i),
                "Makespan": individuoPrimeiraIteracao["makespan"],
                "LoadBalance": individuoPrimeiraIteracao["loadBalance"],
                "Flowtime": individuoPrimeiraIteracao["flowtime"],
                "CommunicationCost": individuoPrimeiraIteracao["communicationCost"],
                "WaitingTime": individuoPrimeiraIteracao["waitingTime"],
                "Fitness": individuoPrimeiraIteracao["fitness"],
                "Alocacao": individuoPrimeiraIteracao["alocacao"],
                "Escalonamento": individuoPrimeiraIteracao["escalonamento"],
            }

            dicUltimaIteracao[str(i)] = {
                "Individuo": str(i),
                "Makespan": individuoUltimaIteracao["makespan"],
                "LoadBalance": individuoUltimaIteracao["loadBalance"],
                "Flowtime": individuoUltimaIteracao["flowtime"],
                "CommunicationCost": individuoUltimaIteracao["communicationCost"],
                "WaitingTime": individuoUltimaIteracao["waitingTime"],
                "Fitness": individuoUltimaIteracao["fitness"],
                "Alocacao": individuoUltimaIteracao["alocacao"],
                "Escalonamento": individuoUltimaIteracao["escalonamento"],
            }

            # dicEscalonamento[str(i)] = {
            #     "Individuo": str(i),
            #     "Alocacao": individuoUltimaIteracao["alocacao"],
            #     "Escalonamento": individuoUltimaIteracao["escalonamento"],
            # }

        colunasIndividuos = [
            "Individuo",
            "Makespan",
            "LoadBalance",
            "Flowtime",
            "CommunicationCost",
            "WaitingTime",
            "Fitness",
            "Alocacao",
            "Escalonamento",
        ]

        dfPrimeiraIteracao = pd.DataFrame.from_dict(
            dicPrimeiraIteracao, columns=colunasIndividuos, orient="index"
        )
        dfPrimeiraIteracao.reset_index(drop=True, inplace=True)

        dfUltimaIteracao = pd.DataFrame.from_dict(dicUltimaIteracao, columns=colunasIndividuos, orient="index"
        )
        dfUltimaIteracao.reset_index(drop=True, inplace=True)

        paramentrosMSEAux = []
        for param, value in parametrosMSE.items():
            paramentrosMSEAux.append(
                {
                    "Parametro": param,
                    "Valor": value,
                }
            )

        dfParametros = pd.DataFrame(paramentrosMSEAux)
        dfParametros[""] = None
        dfParametros.reset_index(drop=True, inplace=True)

        dfResultadosPrimeiraIteracao = pd.concat(
            [dfParametros, dfPrimeiraIteracao], axis=1
        )
        dfResultadosUltimaIteracao = pd.concat([dfParametros, dfUltimaIteracao], axis=1)

        os.makedirs(f"{pastaResultados}/{hashPopulacao}", exist_ok=True)

        dfResultadosPrimeiraIteracao.to_csv(
            f"{pastaResultados}/{hashPopulacao}/primeira_iteracao_{alpha}.csv",
            index=False,
        )
        dfResultadosUltimaIteracao.to_csv(
            f"{pastaResultados}/{hashPopulacao}/ultima_iteracao_{alpha}.csv",
            index=False,
        )

        print(f"Resultados salvos em {hashPopulacao}")

        hashPrimeiraIteracao = salva_populacao(individuosPrimeiraIteracao)
        hashUltimaIteracao = salva_populacao(individuosUltimaIteracao)

        print(f"Hash da primeira iteração: {hashPrimeiraIteracao}")
        print(f"Hash da ultima iteração: {hashUltimaIteracao}")

        return hashPrimeiraIteracao, hashUltimaIteracao
    except Exception as e:
        print("Erro ao salvar resultados")
        return False


def main():

    parametrosPopulacao = {
        "tamanhoPopulacao": 4,
        "grafo": "grafos_experimento/robot-4-20-30.stg",
    }
    
    while True:

        opcao = input("Escolha a opção (1 - salvar, 2 - carregar): ")
        if opcao == "1":
            hashPopulacao = salva(parametrosPopulacao)
            if hashPopulacao:
                print(f"Hash da população: {hashPopulacao}")
        if opcao == "2":

            hashPopulacao = input("Digite o hash da população: ")

            parametrosPopulacao["hashPopulacao"] = hashPopulacao

            parametrosMSE = {
                "numeroIteracoes": 3,
                "chanceCrossoverAlocacao": 0.4,
                "chanceCrossoverEscalonamento": 0.4,
                "chanceMutacaoAlocacao": 0.2,
                "chanceMutacaoEscalonamento": 0.2,
                "taxaElitismo": 0.2,
                "tamanhoPopulacao": parametrosPopulacao["tamanhoPopulacao"],
            }

            populacao = carrega(parametrosPopulacao["hashPopulacao"])
            hashCalculado = gera_hash(populacao)

            if hashCalculado != parametrosPopulacao["hashPopulacao"]:
                print("Hash da população não confere")
                return False

            listaAlphas = ["0", "0.25", "0.5", "0.75", "1"]

            numeroTarefas = ler_numero_tarefas(parametrosPopulacao["grafo"])
            numProcessadores = int(parametrosPopulacao["grafo"].split("-")[1])
            dic = ler_arquivo_ghe(parametrosPopulacao["grafo"], numProcessadores)

            experimento(
                listaAlphas,
                dic,
                parametrosMSE,
                numeroTarefas,
                populacao,
                parametrosPopulacao["hashPopulacao"],
                numProcessadores,
            )



if __name__ == "__main__":
    main()
