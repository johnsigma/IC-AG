from threading import Thread
from time import time
from tkinter import ttk, messagebox, Text, END
import sys
from uuid import uuid4
import pandas as pd
from funcoes import ler_numero_tarefas, ler_arquivo_ghe, makespan, load_balance
from task_scheduling import experimento_breno
from main import experimento

class MSEParametersGUI:
    def __init__(self, root, parametrosMSE):
        self.root = root
        self.root.title("Parâmetros MSE")
        self.parametrosMSE = parametrosMSE
        self.entries = {}
        
        # Dicionário para mapear os parâmetros para labels mais descritivos
        labels = {
            "tamanhoPopulacao": "Tamanho da População",
            "numeroIteracoes": "Número de Iterações",
            "chanceCrossoverAlocacao": "Chance de Crossover de Alocação",
            "chanceCrossoverEscalonamento": "Chance de Crossover de Escalonamento",
            "chanceMutacaoAlocacao": "Chance de Mutação de Alocação",
            "chanceMutacaoEscalonamento": "Chance de Mutação de Escalonamento",
            "taxaElitismo": "Taxa de Elitismo",
        }

        row = 0
        for param, value in parametrosMSE.items():
            label_text = labels.get(param, param)  # Obtém o label descritivo ou usa o nome do parâmetro
            label = ttk.Label(root, text=label_text)
            label.grid(row=row, column=0, padx=10, pady=5, sticky="W")
            entry = ttk.Entry(root)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, padx=10, pady=5)
            self.entries[param] = entry
            row += 1

        save_button = ttk.Button(root, text="Iniciar experimento", command=self.start_experiment)
        save_button.grid(row=row, column=0, columnspan=2, pady=10)
        
        # Adicionar widget de texto para exibir o log
        self.log_text = Text(root, height=20, width=80)
        self.log_text.grid(row=row+1, column=0, columnspan=2, padx=10, pady=10)
        
        # Sobrescrever o comportamento do evento de fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def save_parameters(self):
        try:
            for param, entry in self.entries.items():
                value = entry.get()
                if param in ["tamanhoPopulacao", "numeroIteracoes"]:
                    self.parametrosMSE[param] = int(value)
                else:
                    self.parametrosMSE[param] = float(value) if '.' in value else int(value)
        except ValueError:
            messagebox.showerror("Erro de Validação", f"Valor inválido para {param}: {value}")
            
    def on_closing(self):
        # Interromper a execução do programa ao clicar no 'X'
        self.root.quit()
        sys.exit()
        
    def start_experiment(self):
        self.save_parameters()
        self.log_text.delete(1.0, END)  # Limpar o log antes de iniciar o experimento
        sys.stdout = TextRedirector(self.log_text, "stdout")
        sys.stderr = TextRedirector(self.log_text, "stderr")
        
        experiment_thread = Thread(target=self.run_experiment)
        experiment_thread.start()

    def run_experiment(self):

        inicio = time()
        
        grafoRobot = "grafos_experimento/robot-4-20-30.stg"
        grafoSparse = "grafos_experimento/sparse-4-100-30.stg"
        grafoFpppp = "grafos_experimento/fpppp-8-20-30.stg"
        grafos = [grafoRobot, grafoSparse, grafoFpppp]

        listaAlphas = ["0", "0.25", "0.5", "0.75", "1"]

        print("Experimento: Iniciado")

        hashAleatorio = uuid4().hex

        for grafo in grafos:
            print(f"Experimentos com grafo {grafo}: Iniciado")
            print(f"Experimento com AG: Iniciado")

            numeroTarefas = ler_numero_tarefas(grafo)
            numProcessadores = int(grafo.split("-")[1])
            dic = ler_arquivo_ghe(grafo, numProcessadores)
            dicResultadoMSE = experimento(listaAlphas, dic, self.parametrosMSE, numeroTarefas, numProcessadores)
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
            
            tarefasBrenoIpeft = resultadoBreno['IPEFT'][numeroTarefas][grafo]["escalonamento"]
            tarefasBrenoIheft = resultadoBreno['IHEFT'][numeroTarefas][grafo]["escalonamento"]
            tarefasBrenoCpop = resultadoBreno['CPOP'][numeroTarefas][grafo]["escalonamento"]
            tarefasBrenoHeft = resultadoBreno['HEFT'][numeroTarefas][grafo]["escalonamento"]
            
            makespanBrenoIpeft = makespan(tarefasBrenoIpeft, numProcessadores, dic)
            loadBalanceBrenoIpeft = load_balance(tarefasBrenoIpeft, numProcessadores, dic, makespanBrenoIpeft)
            makespanBrenoIheft = makespan(tarefasBrenoIheft, numProcessadores, dic)
            loadBalanceBrenoIheft = load_balance(tarefasBrenoIheft, numProcessadores, dic, makespanBrenoIheft)
            makespanBrenoCpop = makespan(tarefasBrenoCpop, numProcessadores, dic)
            loadBalanceBrenoCpop = load_balance(tarefasBrenoCpop, numProcessadores, dic, makespanBrenoCpop)
            makespanBrenoHeft = makespan(tarefasBrenoHeft, numProcessadores, dic)
            loadBalanceBrenoHeft = load_balance(tarefasBrenoHeft, numProcessadores, dic, makespanBrenoHeft)
            
            # print(f"Resultados Breno grafo: {grafo}")
            # print(f"Makespan IPEFT (MSE): {makespanBrenoIpeft}")
            # print(f"Makespan IPEFT (Breno): {resultadoBreno['IPEFT'][numeroTarefas][grafo]['makespan']}")
            # print(f"Load Balance IPEFT (MSE): {loadBalanceBrenoIpeft}")
            # print(f"Load Balance IPEFT (Breno): {resultadoBreno['IPEFT'][numeroTarefas][grafo]['loadBalance']}")
            # print(f"Makespan IHEFT (MSE): {makespanBrenoIheft}")
            # print(f"Makespan IHEFT (Breno): {resultadoBreno['IHEFT'][numeroTarefas][grafo]['makespan']}")
            # print(f"Load Balance IHEFT (MSE): {loadBalanceBrenoIheft}")
            # print(f"Load Balance IHEFT (Breno): {resultadoBreno['IHEFT'][numeroTarefas][grafo]['loadBalance']}")
            # print(f"Makespan CPOP (MSE): {makespanBrenoCpop}")
            # print(f"Makespan CPOP (Breno): {resultadoBreno['CPOP'][numeroTarefas][grafo]['makespan']}")
            # print(f"Load Balance CPOP (MSE): {loadBalanceBrenoCpop}")
            # print(f"Load Balance CPOP (Breno): {resultadoBreno['CPOP'][numeroTarefas][grafo]['loadBalance']}")
            # print(f"Makespan HEFT (MSE): {makespanBrenoHeft}")
            # print(f"Makespan HEFT (Breno): {resultadoBreno['HEFT'][numeroTarefas][grafo]['makespan']}")
            # print(f"Load Balance HEFT (MSE): {loadBalanceBrenoHeft}")
            # print(f"Load Balance HEFT (Breno): {resultadoBreno['HEFT'][numeroTarefas][grafo]['loadBalance']}\n\n")
            
            resultadoBreno['IPEFT'][numeroTarefas][grafo]['makespan'] = makespanBrenoIpeft
            resultadoBreno['IPEFT'][numeroTarefas][grafo]['loadBalance'] = loadBalanceBrenoIpeft
            resultadoBreno['IHEFT'][numeroTarefas][grafo]['makespan'] = makespanBrenoIheft
            resultadoBreno['IHEFT'][numeroTarefas][grafo]['loadBalance'] = loadBalanceBrenoIheft
            resultadoBreno['CPOP'][numeroTarefas][grafo]['makespan'] = makespanBrenoCpop
            resultadoBreno['CPOP'][numeroTarefas][grafo]['loadBalance'] = loadBalanceBrenoCpop
            resultadoBreno['HEFT'][numeroTarefas][grafo]['makespan'] = makespanBrenoHeft
            resultadoBreno['HEFT'][numeroTarefas][grafo]['loadBalance'] = loadBalanceBrenoHeft
            
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

            for param, value in self.parametrosMSE.items():              
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

        fim = time()
        tempo_em_segundos = fim - inicio
        tempo_em_minutos = tempo_em_segundos / 60

        # Salvar o tempo de execução com o mesmo hash aleatório
        nomeArquivoTempo = f"resultados/tempo_{hashAleatorio}.txt"
        with open(nomeArquivoTempo, "w", encoding="utf-8") as arquivo:
            arquivo.write(f"Tempo de execucao: {round(tempo_em_minutos, 2)} minutos")

        # Adicionar mensagem de conclusão na interface gráfica
        self.log_text.insert(END, "\nExperimento concluído com sucesso!\n")
        print(f"Tempo de execucao: {round(tempo_em_minutos, 2)} minutos")
        print(f"Tempo salvo em: {nomeArquivoTempo}")
        


class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.insert(END, str)
        self.widget.see(END)
        self.widget.update_idletasks()  # Atualiza a interface gráfica

    def flush(self):
        pass