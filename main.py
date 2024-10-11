from uuid import uuid4
import time
import pandas as pd
import numpy as np
from funcoes import (
    ler_arquivo_ghe,
    ler_numero_tarefas,
)
from MSE import MSE
from task_scheduling import experimento_breno


def experimento(
    listaAlphas, arquivoGrafo, parametrosMSE, numTarefas, numProcessadores=None
):
    if numProcessadores is None:
        numProcessadores = int(arquivoGrafo.split("-")[1])

    dic = ler_arquivo_ghe(arquivoGrafo, numProcessadores)
    dicResultado = {}

    for alpha in listaAlphas:
        dicResultado[alpha] = {}
        dicResultado[alpha]["makespan"] = []
        dicResultado[alpha]["loadBalance"] = []
        dicResultado[alpha]["iteracao"] = []

        for _ in range(1, 2):
            mse = MSE(dic, numTarefas, numProcessadores, float(alpha))
            mediasFitness, mediasMakespan, mediasLoadBalance, melhorIndividuo = (
                mse.inicio(**parametrosMSE)
            )
            dicResultado[alpha]["makespan"].append(melhorIndividuo["makespan"])
            dicResultado[alpha]["loadBalance"].append(melhorIndividuo["loadBalance"])
            dicResultado[alpha]["iteracao"].append(melhorIndividuo["iteracao"])

        dicResultado[alpha]["mediaMakespan"] = np.mean(dicResultado[alpha]["makespan"])
        dicResultado[alpha]["mediaLoadBalance"] = np.mean(
            dicResultado[alpha]["loadBalance"]
        )
        dicResultado[alpha]["mediaIteracao"] = np.mean(dicResultado[alpha]["iteracao"])
        dicResultado[alpha]["desvioPadraoMakespan"] = np.std(
            dicResultado[alpha]["makespan"]
        )
        dicResultado[alpha]["desvioPadraoLoadBalance"] = np.std(
            dicResultado[alpha]["loadBalance"]
        )
        dicResultado[alpha]["desvioPadraoIteracao"] = np.std(
            dicResultado[alpha]["iteracao"]
        )

    return dicResultado


if __name__ == "__main__":
    inicio = time.time()

    grafoRobot = "grafos_experimento/robot-4-20-30.stg"
    grafoSparse = "grafos_experimento/sparse-4-100-30.stg"
    grafoFpppp = "grafos_experimento/fpppp-8-20-30.stg"

    grafos = [grafoRobot, grafoSparse, grafoFpppp]

    parametrosMSE = {
        "tamanhoPopulacao": 20,
        "numeroIteracoes": 2500,
        "chanceCrossoverAlocacao": 0.4,
        "chanceCrossoverEscalonamento": 0.4,
        "chanceMutacaoAlocacao": 0.2,
        "chanceMutacaoEscalonamento": 0.2,
        "taxaElitismo": 0.2,
    }

    listaAlphas = ["0", "0.25", "0.5", "0.75", "1"]

    print("Experimento: Iniciado")

    hashAleatorio = uuid4().hex

    for grafo in grafos:
        print(f"Experimentos com grafo {grafo}: Iniciado")
        print(f"Experimento com AG: Iniciado")

        numeroTarefas = ler_numero_tarefas(grafo)
        dicResultadoMSE = experimento(listaAlphas, grafo, parametrosMSE, numeroTarefas)
        print(f"Experimento com AG: Finalizado")

        splitGrafo = grafo.split("-")
        listaProcessadores = [int(splitGrafo[1])]
        variacaoTempoExecucaoLista = [int(splitGrafo[2])]
        variacaoCustoComunicacaoLista = [int(splitGrafo[3].split(".")[0])]
        numTarefasLista = [numeroTarefas]
        diretorioBase = "grafos_experimento/"

        print("Experimento com IPEFT, IHEFT, CPOP, HEFT: Iniciado")
        resultadoBreno = experimento_breno(
            listaProcessadores,
            variacaoTempoExecucaoLista,
            variacaoCustoComunicacaoLista,
            numTarefasLista,
            diretorioBase,
            5,
            True,
            grafo,
        )
        print("Experimento com IPEFT, IHEFT, CPOP, HEFT: Finalizado")

        resultados = []
        for chave, valor in resultadoBreno.items():
            resultados.append(
                {
                    "Algoritmo": chave,
                    "Makespan": round(valor[numeroTarefas][grafo]["makespan"], 2),
                    "LoadBalance": round(valor[numeroTarefas][grafo]["loadBalance"], 2),
                    "MediaIteracao": "N/A",
                    "DesvioPadraoMakespan": "N/A",
                    "DesvioPadraoLoadBalance": "N/A",
                    "DesvioPadraoIteracao": "N/A",
                }
            )

        for alpha, valor in dicResultadoMSE.items():
            resultados.append(
                {
                    "Algoritmo": f"MSE_{alpha}",
                    "Makespan": round(valor["mediaMakespan"], 2),
                    "LoadBalance": round(valor["mediaLoadBalance"], 2),
                    "MediaIteracao": round(valor["mediaIteracao"], 2),
                    "DesvioPadraoMakespan": round(valor["desvioPadraoMakespan"], 2),
                    "DesvioPadraoLoadBalance": round(
                        valor["desvioPadraoLoadBalance"], 2
                    ),
                    "DesvioPadraoIteracao": round(valor["desvioPadraoIteracao"], 2),
                }
            )

        paramentrosMSEAux = []

        for param, value in parametrosMSE.items():
            paramentrosMSEAux.append(
                {
                    "Parametro": param,
                    "Valor": value,
                }
            )

        nomeGrafo = grafo.split("/")[1]

        df_parametros = pd.DataFrame(paramentrosMSEAux)
        df_parametros[""] = None
        df_resultados = pd.DataFrame(resultados)

        # Criar DataFrame com os resultados e parâmetros
        df_final = pd.concat([df_parametros, df_resultados], axis=1)

        nomeArquivo = f"resultados/{nomeGrafo}_{hashAleatorio}.csv"

        # Salvar o DataFrame em um arquivo CSV
        df_final.to_csv(nomeArquivo, index=False, encoding="utf-8")

        print(f"Resultados salvos em: {nomeArquivo}")

        print(f"Experimentos com grafo {grafo}: Finalizado")

    print("Experimento: Finalizado")

    fim = time.time()
    tempo_em_segundos = fim - inicio
    tempo_em_minutos = tempo_em_segundos / 60

    # Salvar o tempo de execução com o mesmo hash aleatório
    nomeArquivoTempo = f"resultados/tempo_{hashAleatorio}.txt"
    with open(nomeArquivoTempo, "w", encoding="utf-8") as arquivo:
        arquivo.write(f"Tempo de execucao: {round(tempo_em_minutos, 2)} minutos")

    print(f"Tempo de execucao: {round(tempo_em_minutos, 2)} minutos")
    print(f"Tempo salvo em: {nomeArquivoTempo}")
