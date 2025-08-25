import os
import random
from sys import argv
from time import time
from uuid import uuid4
from datetime import datetime
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
        # salvar_populacao_csv(populacao, f"populacao_{hashPopulacao}.csv")
        return hashPopulacao
    except:
        print("Erro ao salvar")
        return False


def salvar_populacao_csv(populacao, nome_arquivo):
    dados = []
    for i, individuo in enumerate(populacao):
        dados.append({
            "Individuo": i,
            "Makespan": individuo.get("makespan"),
            "LoadBalance": individuo.get("loadBalance"),
            "Flowtime": individuo.get("flowtime"),
            "CommunicationCost": individuo.get("communicationCost"),
            "WaitingTime": individuo.get("waitingTime"),
            "Fitness": individuo.get("fitness"),
            "Alocacao": individuo.get("alocacao"),
            "Escalonamento": individuo.get("escalonamento"),
        })
    df = pd.DataFrame(dados)
    df.to_csv(nome_arquivo, index=False)


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
    pastaResultados: str = "resultados2",
    runId: str | None = None,
):
    resultados = {}
    hashes_ultima_iteracao = []
    # Gera runId uma unica vez por execucao (se nao fornecido)
    if runId is None:
        base_hash_dir = os.path.join(pastaResultados, hashPopulacao)
        os.makedirs(base_hash_dir, exist_ok=True)
        existentes = [
            d for d in os.listdir(base_hash_dir)
            if os.path.isdir(os.path.join(base_hash_dir, d)) and d.startswith("run_")
        ]
        max_n = 0
        for d in existentes:
            try:
                n = int(d.split("run_")[-1])
                if n > max_n:
                    max_n = n
            except Exception:
                continue
        runId = f"run_{max_n + 1:03d}"

    for alpha in listaAlphas:

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

        hashPrimeiraIteracao, hashUltimaIteracao = salva_resultados(
            resultadosExperimento["primeiraIteracao"],
            resultadosExperimento["ultimaIteracao"],
            parametrosMSE,
            hashPopulacao,
            alpha,
            pastaResultados,
            runId,
        )

        # Coleta o hash da última iteração para este alpha
        if hashUltimaIteracao:
            hashes_ultima_iteracao.append(
                f"Alpha {alpha}: {hashUltimaIteracao}")

    return hashes_ultima_iteracao


def salva_resultados(
    individuosPrimeiraIteracao,
    individuosUltimaIteracao,
    parametrosMSE,
    hashPopulacao,
    alpha,
    pastaResultados: str = "resultados2",
    runId: str | None = None,
):
    try:
        # Define subpasta por execução para não sobrescrever resultados anteriores
        base_hash_dir = os.path.join(pastaResultados, hashPopulacao)
        os.makedirs(base_hash_dir, exist_ok=True)
        if not runId:
            # Gera um identificador incremental: run_001, run_002, ...
            existentes = [
                d for d in os.listdir(base_hash_dir)
                if os.path.isdir(os.path.join(base_hash_dir, d)) and d.startswith("run_")
            ]
            max_n = 0
            for d in existentes:
                try:
                    n = int(d.split("run_")[-1])
                    if n > max_n:
                        max_n = n
                except Exception:
                    continue
            runId = f"run_{max_n + 1:03d}"

        dicPrimeiraIteracao = {}
        dicUltimaIteracao = {}

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

        dfUltimaIteracao = pd.DataFrame.from_dict(
            dicUltimaIteracao, columns=colunasIndividuos, orient="index"
        )
        dfUltimaIteracao.reset_index(drop=True, inplace=True)

        paramentrosMSEAux = []
        for param, value in parametrosMSE.items():
            paramentrosMSEAux.append({"Parametro": param, "Valor": value})

        dfParametros = pd.DataFrame(paramentrosMSEAux)
        dfParametros[""] = None
        dfParametros.reset_index(drop=True, inplace=True)

        dfResultadosPrimeiraIteracao = pd.concat(
            [dfParametros, dfPrimeiraIteracao], axis=1
        )
        dfResultadosUltimaIteracao = pd.concat(
            [dfParametros, dfUltimaIteracao], axis=1
        )

        # Cria subpasta por execução: resultados2/<hash>/<runId>/
        pasta_execucao = os.path.join(base_hash_dir, runId)
        os.makedirs(pasta_execucao, exist_ok=True)

        dfResultadosPrimeiraIteracao.to_csv(
            os.path.join(pasta_execucao, f"primeira_iteracao_{alpha}.csv"),
            index=False,
        )
        dfResultadosUltimaIteracao.to_csv(
            os.path.join(pasta_execucao, f"ultima_iteracao_{alpha}.csv"),
            index=False,
        )

        print(f"Resultados salvos em {hashPopulacao}/{runId}")

        # Salva apenas a população da última iteração (a primeira é redundante)
        hashUltimaIteracao = salva_populacao(individuosUltimaIteracao)

        return None, hashUltimaIteracao
    except Exception:
        print("Erro ao salvar resultados")
        return False


def main():

    parametrosPopulacao = {
        "tamanhoPopulacao": 10,
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
                "numeroIteracoes": 10,
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

            listaAlphas = ["0.5"]

            numeroTarefas = ler_numero_tarefas(parametrosPopulacao["grafo"])
            numProcessadores = int(parametrosPopulacao["grafo"].split("-")[1])
            dic = ler_arquivo_ghe(
                parametrosPopulacao["grafo"], numProcessadores)

            hashsPopulacao = experimento(
                listaAlphas,
                dic,
                parametrosMSE,
                numeroTarefas,
                populacao,
                parametrosPopulacao["hashPopulacao"],
                numProcessadores,
            )

            print("Experimento concluído com sucesso!")
            print("Hashs das últimas iterações:")
            for hashStr in hashsPopulacao:
                print(hashStr)


if __name__ == "__main__":
    main()
