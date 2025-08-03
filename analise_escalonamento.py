import pandas as pd
import ast


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

            # Ignora as tarefas fictícias de início e fim (0 e num_tarefas_reais + 1)
            if id_tarefa == 0 or id_tarefa > num_tarefas_reais:
                continue

            num_processadores = int(linhas[0].strip().split()[1])
            num_predecessoras = int(partes[1 + num_processadores])
            predecessoras = []
            if num_predecessoras > 0:
                # Pega os IDs das tarefas predecessoras
                inicio_preds = 2 + num_processadores
                for j in range(num_predecessoras):
                    pred_id = int(partes[inicio_preds + j * 2])
                    predecessoras.append(pred_id)

            grafo[id_tarefa] = predecessoras

    return grafo, num_tarefas_reais


def validar_escalonamento(escalonamento, grafo, num_tarefas_reais):
    """
    Valida um único escalonamento com base no grafo de dependências,
    considerando que as tarefas fictícias (0 e final) são obrigatórias no início e fim.
    """
    # 1. Verificar se a tarefa inicial é a primeira
    if not escalonamento or escalonamento[0] != 0:
        return False, "A tarefa fictícia inicial (0) não é a primeira do escalonamento."

    # 2. Verificar se a tarefa final é a última
    tarefa_final_id = num_tarefas_reais + 1
    if escalonamento[-1] != tarefa_final_id:
        return False, f"A tarefa fictícia final ({tarefa_final_id}) não é a última do escalonamento."

    # 3. Verificar se todas as tarefas REAIS estão presentes no escalonamento
    tarefas_reais_no_escalonamento = {
        t for t in escalonamento if t != 0 and t != tarefa_final_id}
    tarefas_no_grafo = set(grafo.keys())

    if tarefas_reais_no_escalonamento != tarefas_no_grafo:
        tarefas_faltando = tarefas_no_grafo - tarefas_reais_no_escalonamento
        tarefas_extras = tarefas_reais_no_escalonamento - tarefas_no_grafo
        return False, f"Inconsistência nas tarefas reais. Faltando: {tarefas_faltando}. Extras: {tarefas_extras}"

    # 4. Verificar a ordem das predecessoras para as tarefas reais
    posicoes = {tarefa: i for i, tarefa in enumerate(escalonamento)}
    for tarefa, predecessoras in grafo.items():
        if not predecessoras:
            continue
        posicao_tarefa = posicoes[tarefa]
        for pred in predecessoras:
            # A tarefa fictícia 0 pode ser uma predecessora, e deve vir antes
            if pred not in posicoes or posicoes[pred] > posicao_tarefa:
                return False, f"Erro de precedência para Tarefa {tarefa}: a predecessora {pred} não vem antes."

    return True, "Válido"


def analisar_populacao(caminho_csv, caminho_stg):
    """
    Lê o CSV da população e o grafo, valida o escalonamento de cada indivíduo,
    imprime apenas os inválidos e mostra uma estatística no final.
    """
    try:
        df = pd.read_csv(caminho_csv)
        # Converter a string do escalonamento para uma lista de inteiros, garantindo que os elementos são int
        df['Escalonamento'] = df['Escalonamento'].apply(
            lambda x: [int(i) for i in ast.literal_eval(x)])
    except FileNotFoundError:
        print(f"Erro: Arquivo CSV '{caminho_csv}' não encontrado.")
        return
    except Exception as e:
        print(f"Erro ao ler ou processar o arquivo CSV: {e}")
        return

    try:
        grafo, num_tarefas_reais = ler_grafo_stg(caminho_stg)
    except FileNotFoundError:
        print(f"Erro: Arquivo STG '{caminho_stg}' não encontrado.")
        return
    except Exception as e:
        print(f"Erro ao ler ou processar o arquivo STG: {e}")
        return

    print(f"Analisando escalonamentos do arquivo: {caminho_csv}")
    print(f"Com base no grafo: {caminho_stg}\n")

    invalidos = []
    validos_count = 0
    total_individuos = len(df)

    for index, row in df.iterrows():
        individuo_id = row['Individuo']
        escalonamento = row['Escalonamento']

        eh_valido, mensagem = validar_escalonamento(
            escalonamento, grafo, num_tarefas_reais)

        if eh_valido:
            validos_count += 1
        else:
            invalidos.append((individuo_id, mensagem))

    if invalidos:
        print("--- Indivíduos Inválidos Encontrados ---")
        for individuo_id, mensagem in invalidos:
            print(f"Indivíduo {individuo_id}:")
            print(f"  - Motivo: {mensagem}")
            print("-" * 20)
    else:
        print("--- Nenhum indivíduo inválido encontrado ---")

    print("\n--- Análise Estatística ---")
    invalidos_count = len(invalidos)

    if total_individuos > 0:
        percentual_validos = (validos_count / total_individuos) * 100
        percentual_invalidos = (invalidos_count / total_individuos) * 100
        print(f"Total de indivíduos analisados: {total_individuos}")
        print(
            f"Indivíduos Válidos: {validos_count} ({percentual_validos:.2f}%)")
        print(
            f"Indivíduos Inválidos: {invalidos_count} ({percentual_invalidos:.2f}%)")
    else:
        print("Nenhum indivíduo para analisar.")


if __name__ == '__main__':
    # Caminhos para os arquivos anexados na conversa
    arquivo_csv = 'populacao_e8ea2d0478c2ebf824a67eea94e7b514924d370c136660782654097237779f64.csv'
    arquivo_stg = 'grafos_experimento/robot-4-20-30.stg'

    analisar_populacao(arquivo_csv, arquivo_stg)
