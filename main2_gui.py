import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from main2 import salva, carrega, experimento
from funcoes import ler_numero_tarefas, ler_arquivo_ghe
import os

class Main2GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface Gráfica - main2.py")
        self.root.geometry("400x400")  # Define o tamanho da janela para 800x600 pixels

        # Parâmetros iniciais
        self.parametrosPopulacao = {
            "tamanhoPopulacao": tk.IntVar(value=4),
            "grafo": tk.StringVar(value="grafos_experimento/robot-4-20-30.stg"),
        }
        self.parametrosMSE = {
            "numeroIteracoes": tk.IntVar(value=3),
            "chanceCrossoverAlocacao": tk.DoubleVar(value=0.4),
            "chanceCrossoverEscalonamento": tk.DoubleVar(value=0.4),
            "chanceMutacaoAlocacao": tk.DoubleVar(value=0.2),
            "chanceMutacaoEscalonamento": tk.DoubleVar(value=0.2),
            "taxaElitismo": tk.DoubleVar(value=0.2),
        }
        self.alphas = tk.StringVar(value="0,0.25,0.5,0.75,1")

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # Tamanho da População
        ttk.Label(self.root, text="Tamanho da População:").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.parametrosPopulacao["tamanhoPopulacao"]).grid(row=0, column=1)

        # Caminho do Grafo
        ttk.Label(self.root, text="Caminho do Grafo:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.parametrosPopulacao["grafo"]).grid(row=1, column=1)

        # Parâmetros do MSE
        ttk.Label(self.root, text="Número de Iterações:").grid(row=2, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.parametrosMSE["numeroIteracoes"]).grid(row=2, column=1)

        ttk.Label(self.root, text="Chance Crossover Alocação:").grid(row=3, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.parametrosMSE["chanceCrossoverAlocacao"]).grid(row=3, column=1)

        ttk.Label(self.root, text="Chance Crossover Escalonamento:").grid(row=4, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.parametrosMSE["chanceCrossoverEscalonamento"]).grid(row=4, column=1)

        ttk.Label(self.root, text="Chance Mutação Alocação:").grid(row=5, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.parametrosMSE["chanceMutacaoAlocacao"]).grid(row=5, column=1)

        ttk.Label(self.root, text="Chance Mutação Escalonamento:").grid(row=6, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.parametrosMSE["chanceMutacaoEscalonamento"]).grid(row=6, column=1)

        ttk.Label(self.root, text="Taxa de Elitismo:").grid(row=7, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.parametrosMSE["taxaElitismo"]).grid(row=7, column=1)

        # Alphas
        ttk.Label(self.root, text="Alphas (separados por vírgulas):").grid(row=8, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.alphas).grid(row=8, column=1)

        # Botões
        ttk.Button(self.root, text="Salvar População", command=self.salvar_populacao).grid(row=9, column=0, pady=10)
        ttk.Button(self.root, text="Carregar População", command=self.carregar_populacao).grid(row=9, column=1, pady=10)
        ttk.Button(self.root, text="Rodar Experimento", command=self.rodar_experimento).grid(row=10, column=0, columnspan=2, pady=10)

    def salvar_populacao(self):
        hash_populacao = salva({
            "tamanhoPopulacao": self.parametrosPopulacao["tamanhoPopulacao"].get(),
            "grafo": self.parametrosPopulacao["grafo"].get(),
        })
        if hash_populacao:
            messagebox.showinfo("Sucesso", f"População salva com hash: {hash_populacao}")
        else:
            messagebox.showerror("Erro", "Erro ao salvar a população.")

    def carregar_populacao(self):
        hash_populacao = simpledialog.askstring("Carregar População", "Digite o hash da população:")
        if not hash_populacao:
            return

        self.populacao = carrega(hash_populacao)
        if not self.populacao:
            messagebox.showerror("Erro", "Erro ao carregar a população.")
            return

        self.hash_populacao = hash_populacao
        tamanho_populacao = len(self.populacao)
        self.parametrosPopulacao["tamanhoPopulacao"].set(tamanho_populacao)
        messagebox.showinfo("Sucesso", "População carregada com sucesso!")

    def rodar_experimento(self):
        if not hasattr(self, "populacao") or not self.populacao:
            messagebox.showerror("Erro", "Carregue uma população antes de rodar o experimento.")
            return

        grafo = self.parametrosPopulacao["grafo"].get()
        num_tarefas = ler_numero_tarefas(grafo)
        num_processadores = int(grafo.split("-")[1])
        dic = ler_arquivo_ghe(grafo, num_processadores)

        try:
            lista_alphas = [float(alpha.strip()) for alpha in self.alphas.get().split(",")]
        except ValueError:
            messagebox.showerror("Erro", "Os alphas devem ser números separados por vírgulas.")
            return
        
        parametros = {key: var.get() for key, var in self.parametrosMSE.items()}
        parametros["tamanhoPopulacao"] = self.parametrosPopulacao["tamanhoPopulacao"].get()

        experimento(
            lista_alphas,
            dic,
            parametros,
            num_tarefas,
            self.populacao,
            self.hash_populacao,
            num_processadores,
        )
        messagebox.showinfo("Sucesso", "Experimento concluído com sucesso!")


if __name__ == "__main__":
    root = tk.Tk()
    app = Main2GUI(root)
    root.mainloop()