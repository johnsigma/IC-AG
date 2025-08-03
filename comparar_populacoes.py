import pandas as pd
import ast
import sys

# Funções de validação reutilizadas de outros scripts


def ler_grafo_stg(caminho_arquivo):
    """
    Lê um arquivo de grafo no formato .stg e retorna um dicionário
    com as informações de tarefas e suas predecessoras.
    """
    grafo = {}
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
        num_tarefas_reais, _ = map(int, linhas[0].strip().split())

        for i in range(2, len(linhas)):
            partes = linhas[i].strip().split()
            if not partes:
                continue
            id_tarefa = int(partes[0])
            if id_tarefa == 0 or id_tarefa > num_tarefas_reais:
                continue
            num_processadores = int(linhas[0].strip().split()[1])
            num_predecessoras = int(partes[1 + num_processadores])
            predecessoras = []
            if num_predecessoras > 0:
                inicio_preds = 2 + num_processadores
                for j in range(num_predecessoras):
                    pred_id = int(partes[inicio_preds + j * 2])
                    predecessoras.append(pred_id)
            grafo[id_tarefa] = predecessoras
    return grafo, num_tarefas_reais


def validar_escalonamento(escalonamento, grafo, num_tarefas_reais):
    """
    Valida um único escalonamento com base no grafo de dependências.
    """
    tarefa_final_id = num_tarefas_reais + 1
    if not escalonamento or escalonamento[0] != 0:
        return False, "A tarefa fictícia inicial (0) não é a primeira."
    if escalonamento[-1] != tarefa_final_id:
        return False, f"A tarefa fictícia final ({tarefa_final_id}) não é a última."

    tarefas_reais_no_escalonamento = {
        t for t in escalonamento if t != 0 and t != tarefa_final_id}
    tarefas_no_grafo = set(grafo.keys())
    if tarefas_reais_no_escalonamento != tarefas_no_grafo:
        return False, f"Inconsistência nas tarefas. Faltando: {tarefas_no_grafo - tarefas_reais_no_escalonamento}. Extras: {tarefas_reais_no_escalonamento - tarefas_no_grafo}"

    posicoes = {tarefa: i for i, tarefa in enumerate(escalonamento)}
    for tarefa, predecessoras in grafo.items():
        if not predecessoras:
            continue
        posicao_tarefa = posicoes[tarefa]
        for pred in predecessoras:
            if pred not in posicoes or posicoes[pred] > posicao_tarefa:
                return False, f"Erro de precedência para Tarefa {tarefa}: predecessora {pred} não vem antes."
    return True, "Válido"


def analisar_validade_arquivo(caminho_csv, grafo, num_tarefas_reais, nome_arquivo_desc):
    """Analisa a validade de todos os indivíduos em um único arquivo CSV."""
    print(f"--- Analisando Validade: {nome_arquivo_desc} ---")
    try:
        # O CSV da população inicial não tem o mesmo header que o da iteração
        if "populacao_" in caminho_csv:
            df = pd.read_csv(caminho_csv)
        else:
            df = pd.read_csv(caminho_csv, header=0)

        df['Escalonamento'] = df['Escalonamento'].apply(
            lambda x: [int(i) for i in ast.literal_eval(x)])
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: {caminho_csv}")
        return False, None
    except Exception as e:
        print(f"Erro ao processar {caminho_csv}: {e}")
        return False, None

    total_individuos = len(df)
    invalidos_count = 0
    for index, row in df.iterrows():
        eh_valido, _ = validar_escalonamento(
            row['Escalonamento'], grafo, num_tarefas_reais)
        if not eh_valido:
            invalidos_count += 1

    if invalidos_count == 0:
        print(
            f"Resultado: SUCESSO! Todos os {total_individuos} indivíduos são válidos.\n")
        return True, df
    else:
        print(
            f"Resultado: FALHA! Encontrados {invalidos_count} de {total_individuos} indivíduos inválidos.\n")
        return False, df


def comparar_escalonamentos(df1, df2):
    """Compara a coluna 'Escalonamento' de dois DataFrames."""
    print("--- Comparando Escalonamentos ---")
    if len(df1) != len(df2):
        print(
            f"FALHA: Número de indivíduos diferente. Pop. Inicial: {len(df1)}, 1ª Iteração: {len(df2)}")
        return

    diferencas = 0
    for i in range(len(df1)):
        esc1 = df1.loc[i, 'Escalonamento']
        esc2 = df2.loc[i, 'Escalonamento']
        if esc1 != esc2:
            diferencas += 1
            # print(f"  - Indivíduo {i}: Escalonamentos diferentes.")
            # print(f"    Pop. Inicial: {esc1}")
            # print(f"    1ª Iteração:  {esc2}")

    if diferencas == 0:
        print("Resultado: SUCESSO! Todos os escalonamentos são idênticos entre os dois arquivos.")
    else:
        print(
            f"Resultado: FALHA! {diferencas} de {len(df1)} indivíduos têm escalonamentos diferentes.")


if __name__ == "__main__":

    csv_pop_inicial = "populacao_4d85532b92482df5d8a305c20e7e0cdf5eb988da8f4e8b6a31644a9b32b2c427.csv"
    csv_primeira_iteracao = "resultados2/4d85532b92482df5d8a305c20e7e0cdf5eb988da8f4e8b6a31644a9b32b2c427/primeira_iteracao_0.5.csv"
    arquivo_stg = "grafos_experimento/robot-4-20-30.stg"

    try:
        grafo, num_tarefas_reais = ler_grafo_stg(arquivo_stg)
    except Exception as e:
        print(f"Erro fatal ao ler o arquivo de grafo {arquivo_stg}: {e}")
        sys.exit(1)

    # Validar população inicial
    valido1, df_pop_inicial = analisar_validade_arquivo(
        csv_pop_inicial, grafo, num_tarefas_reais, "População Inicial")

    # Validar primeira iteração
    valido2, df_primeira_iteracao = analisar_validade_arquivo(
        csv_primeira_iteracao, grafo, num_tarefas_reais, "Primeira Iteração")

    # Comparar se ambos os dataframes foram carregados com sucesso
    if df_pop_inicial is not None and df_primeira_iteracao is not None:
        comparar_escalonamentos(df_pop_inicial, df_primeira_iteracao)
