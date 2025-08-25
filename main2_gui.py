import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from main2 import salva, carrega, experimento
from funcoes import ler_numero_tarefas, ler_arquivo_ghe
import os


class MainGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface Gráfica Otimizada")
        self.root.geometry("500x550")

        # Variáveis de estado
        self.populacao = None
        self.hash_populacao = None
        self.caminho_populacao_carregada = tk.StringVar(
            value="Nenhuma população carregada.")

        # --- Variáveis Tkinter ---
        self.parametrosPopulacao = {
            "tamanhoPopulacao": tk.IntVar(value=10),
            "grafo": tk.StringVar(value="grafos_experimento/robot-4-20-30.stg"),
        }
        self.parametrosMSE = {
            "numeroIteracoes": tk.IntVar(value=100),
            "chanceCrossoverAlocacao": tk.DoubleVar(value=0.4),
            "chanceCrossoverEscalonamento": tk.DoubleVar(value=0.4),
            "chanceMutacaoAlocacao": tk.DoubleVar(value=0.2),
            "chanceMutacaoEscalonamento": tk.DoubleVar(value=0.2),
            "taxaElitismo": tk.DoubleVar(value=0.1),
        }
        self.alphas = tk.StringVar(value="0.5")

        self.create_widgets()

    def create_widgets(self):
        # --- Estrutura de Abas ---
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, padx=10, expand=True, fill="both")

        tab_populacao = ttk.Frame(notebook)
        tab_experimento = ttk.Frame(notebook)

        notebook.add(tab_populacao, text="1. Gerenciar População")
        notebook.add(tab_experimento, text="2. Executar Experimento")

        # --- Aba 1: Gerenciar População ---
        self.create_tab_populacao(tab_populacao)

        # --- Aba 2: Executar Experimento ---
        self.create_tab_experimento(tab_experimento)

    def create_tab_populacao(self, tab):
        # --- Frame para Geração de População ---
        frame_gerar = ttk.LabelFrame(
            tab, text="Gerar Nova População", padding=(10, 5))
        frame_gerar.pack(pady=10, padx=10, fill="x")

        ttk.Label(frame_gerar, text="Tamanho da População:").grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_gerar, textvariable=self.parametrosPopulacao["tamanhoPopulacao"], width=30).grid(
            row=0, column=1, sticky="ew", padx=5)

        ttk.Label(frame_gerar, text="Arquivo de Grafo (.stg):").grid(
            row=1, column=0, sticky="w", padx=5, pady=2)
        entry_grafo = ttk.Entry(
            frame_gerar, textvariable=self.parametrosPopulacao["grafo"], width=30)
        entry_grafo.grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(frame_gerar, text="Selecionar...",
                   command=self.selecionar_arquivo_grafo).grid(row=1, column=2, padx=5)

        ttk.Button(frame_gerar, text="Gerar e Salvar População", command=self.salvar_populacao).grid(
            row=2, column=0, columnspan=3, pady=10)

        # --- Frame para Carregamento de População ---
        frame_carregar = ttk.LabelFrame(
            tab, text="Carregar População Existente", padding=(10, 5))
        frame_carregar.pack(pady=10, padx=10, fill="x")

        ttk.Button(frame_carregar, text="Carregar de Arquivo (.pkl)",
                   command=self.carregar_populacao_de_arquivo).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(frame_carregar, text="Carregar por Hash",
                   command=self.carregar_populacao_por_hash).grid(row=0, column=1, padx=5, pady=5)

    def create_tab_experimento(self, tab):
        # --- Frame de Status da População ---
        frame_status = ttk.LabelFrame(
            tab, text="Status da População", padding=(10, 5))
        frame_status.pack(pady=10, padx=10, fill="x")

        ttk.Label(frame_status, textvariable=self.caminho_populacao_carregada,
                  foreground="blue", wraplength=450, justify="left").pack(padx=5, pady=5)

        # --- Frame para Parâmetros do MSE ---
        frame_params = ttk.LabelFrame(
            tab, text="Parâmetros do Algoritmo Genético", padding=(10, 5))
        frame_params.pack(pady=10, padx=10, fill="x")

        params_mse = [
            ("Número de Iterações:", "numeroIteracoes"),
            ("Chance Crossover Alocação:", "chanceCrossoverAlocacao"),
            ("Chance Crossover Escalonamento:", "chanceCrossoverEscalonamento"),
            ("Chance Mutação Alocação:", "chanceMutacaoAlocacao"),
            ("Chance Mutação Escalonamento:", "chanceMutacaoEscalonamento"),
            ("Taxa de Elitismo:", "taxaElitismo"),
        ]

        for i, (text, key) in enumerate(params_mse):
            ttk.Label(frame_params, text=text).grid(
                row=i, column=0, sticky="w", padx=5, pady=2)
            ttk.Entry(frame_params, textvariable=self.parametrosMSE[key]).grid(
                row=i, column=1, sticky="ew", padx=5)

        # --- Frame para Alphas ---
        frame_alphas = ttk.LabelFrame(
            tab, text="Parâmetros de Execução", padding=(10, 5))
        frame_alphas.pack(pady=10, padx=10, fill="x")

        ttk.Label(frame_alphas, text="Alphas (separados por vírgula):").grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_alphas, textvariable=self.alphas).grid(
            row=0, column=1, sticky="ew", padx=5)

        # --- Botão de Execução ---
        ttk.Button(tab, text="Rodar Experimento",
                   command=self.rodar_experimento).pack(pady=20)

    def selecionar_arquivo_grafo(self):
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo de grafo",
            filetypes=(("STG files", "*.stg"), ("All files", "*.*")),
            initialdir=os.path.join(os.getcwd(), "grafos_experimento")
        )
        if filepath:
            # Converte para caminho relativo se estiver dentro do diretório de trabalho
            rel_path = os.path.relpath(filepath, os.getcwd())
            self.parametrosPopulacao["grafo"].set(rel_path.replace("\\", "/"))

    def salvar_populacao(self):
        try:
            params = {
                "tamanhoPopulacao": self.parametrosPopulacao["tamanhoPopulacao"].get(),
                "grafo": self.parametrosPopulacao["grafo"].get(),
            }
            if not os.path.exists(params["grafo"]):
                messagebox.showerror(
                    "Erro", f"Arquivo de grafo não encontrado: {params['grafo']}")
                return

            hash_populacao = salva(params)
            if hash_populacao:
                messagebox.showinfo(
                    "Sucesso", f"População gerada e salva com sucesso!\nHash: {hash_populacao}")
                # Carrega a população recém-criada
                self.carregar_populacao_por_hash(hash_populacao)
            else:
                messagebox.showerror(
                    "Erro", "Ocorreu um erro ao salvar a população.")
        except Exception as e:
            messagebox.showerror(
                "Erro Inesperado", f"Falha ao salvar população: {e}")

    def carregar_populacao_de_arquivo(self):
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo de população",
            filetypes=(("Pickle files", "*.pkl"), ("All files", "*.*")),
            initialdir=os.path.join(os.getcwd(), "populacoes")
        )
        if not filepath:
            return

        hash_populacao = os.path.basename(filepath).replace(
            "populacao_", "").replace(".pkl", "")
        self.carregar_populacao_por_hash(hash_populacao, filepath)

    def carregar_populacao_por_hash(self, hash_externo=None, caminho_arquivo=""):
        if hash_externo:
            hash_populacao = hash_externo
        else:
            hash_populacao = simpledialog.askstring(
                "Carregar População", "Digite o hash da população:")

        if not hash_populacao:
            return

        pop = carrega(hash_populacao)
        if not pop:
            messagebox.showerror(
                "Erro", f"Não foi possível carregar a população com o hash: {hash_populacao}")
            return

        self.populacao = pop
        self.hash_populacao = hash_populacao
        self.parametrosPopulacao["tamanhoPopulacao"].set(len(self.populacao))

        if caminho_arquivo:
            # Se carregado de arquivo, extrair apenas o hash limpo
            nome_arquivo = os.path.basename(caminho_arquivo)
            hash_limpo = nome_arquivo.replace(
                "populacao_", "").replace(".pkl", "")
            display_path = f"Hash: {hash_limpo}"
        else:
            display_path = f"Hash: {self.hash_populacao}"
        self.caminho_populacao_carregada.set(
            f"População Carregada: {display_path}")

        messagebox.showinfo("Sucesso", "População carregada com sucesso!")

    def rodar_experimento(self):
        if not self.populacao:
            messagebox.showerror(
                "Erro", "Nenhuma população carregada. Por favor, gere ou carregue uma população na Aba 1.")
            return

        try:
            grafo = self.parametrosPopulacao["grafo"].get()
            if not os.path.exists(grafo):
                messagebox.showerror(
                    "Erro", f"Arquivo de grafo não encontrado: {grafo}\nVerifique o caminho na Aba 1.")
                return

            num_tarefas = ler_numero_tarefas(grafo)
            num_processadores = int(grafo.split("-")[1])
            dic = ler_arquivo_ghe(grafo, num_processadores)

            lista_alphas = [float(alpha.strip())
                            for alpha in self.alphas.get().split(",")]

            params_mse = {key: var.get()
                          for key, var in self.parametrosMSE.items()}
            params_mse["tamanhoPopulacao"] = len(self.populacao)

            messagebox.showinfo(
                "Iniciando Experimento", "O experimento será executado. Isso pode levar algum tempo.")

            # A função 'experimento' agora salva resultados em subpastas por execução: resultados2/<hash>/<runId>/
            hashes_ultima_iteracao = experimento(
                lista_alphas,
                dic,
                params_mse,
                num_tarefas,
                self.populacao,
                self.hash_populacao,
                num_processadores,
            )

            # Exibe os hashes das últimas iterações
            if hashes_ultima_iteracao:
                hashes_texto = "\n".join(hashes_ultima_iteracao)
                messagebox.showinfo(
                    "Experimento Concluído",
                    f"Experimento concluído com sucesso!\n\nHashes das últimas iterações:\n{hashes_texto}")
            else:
                messagebox.showinfo(
                    "Sucesso", "Experimento concluído com sucesso!")

        except ValueError as e:
            messagebox.showerror(
                "Erro de Valor", f"Verifique os parâmetros. Detalhes: {e}")
        except Exception as e:
            messagebox.showerror(
                "Erro Inesperado", f"Ocorreu um erro durante o experimento: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainGUI(root)
    root.mainloop()
