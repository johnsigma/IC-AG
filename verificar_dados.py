import pandas as pd
import pickle
import ast
from funcoes import carrega_populacao


def comparar_fontes_dados():
    """
    Compara o escalonamento do primeiro indivíduo de um arquivo .pkl e de um .csv.
    """
    hash_populacao = "b80012a962df007d2b42db5b3aa789c6dcbc30c16834ddd05b9a785a22de90b0"
    caminho_pkl = f"populacoes/populacao_{hash_populacao}.pkl"
    caminho_csv = f"resultados2/{hash_populacao}/primeira_iteracao_0.5.csv"

    print(f"Comparando dados para o hash: {hash_populacao}\n")

    # --- Carregar dados do arquivo .pkl ---
    try:
        populacao_pkl = carrega_populacao(hash_populacao)
        if not populacao_pkl:
            print(f"Não foi possível carregar o arquivo PKL: {caminho_pkl}")
            return

        # O escalonamento no pkl já é uma lista de inteiros
        escalonamento_pkl = populacao_pkl[0]['escalonamento']
        print(
            f"Escalonamento do Indivíduo 0 (do arquivo PKL):\n{escalonamento_pkl}\n")
    except Exception as e:
        print(
            f"Erro ao carregar ou processar o arquivo PKL '{caminho_pkl}': {e}")
        return

    # --- Carregar dados do arquivo .csv ---
    try:
        df_csv = pd.read_csv(caminho_csv, header=0)
        # A coluna 'Escalonamento' no CSV é uma string de uma lista de strings
        escalonamento_str_csv = df_csv.loc[0, 'Escalonamento']
        # Convertendo para lista de inteiros
        escalonamento_csv = [int(i)
                             for i in ast.literal_eval(escalonamento_str_csv)]
        print(
            f"Escalonamento do Indivíduo 0 (do arquivo CSV 'primeira_iteracao'):\n{escalonamento_csv}\n")
    except Exception as e:
        print(
            f"Erro ao carregar ou processar o arquivo CSV '{caminho_csv}': {e}")
        return

    # --- Comparação ---
    if escalonamento_pkl == escalonamento_csv:
        print("--- CONCLUSÃO: Os escalonamentos são IDÊNTICOS. ---")
        print("A população inicial do experimento é a mesma que a salva no CSV da primeira iteração.")
    else:
        print("--- CONCLUSÃO: Os escalonamentos são DIFERENTES. ---")
        print("A população no arquivo .pkl não corresponde à população no CSV da primeira iteração.")


if __name__ == '__main__':
    comparar_fontes_dados()
