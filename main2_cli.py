"""
CLI para executar as funcionalidades do main2.py via uma unica linha de comando.

Funcionalidades:
    - salvar: gera uma populacao inicial e salva; imprime o hash gerado.
    - carregar: carrega uma populacao pelo hash e roda o experimento; imprime os hashes das ultimas iteracoes (um por alpha).
    - salvar-executar: gera e salva uma populacao e, em seguida, roda o experimento com essa populacao recem-gerada.
    - docs: exibe documentacao rapida de uso e exemplos.

Decisao sobre parametros do AG:
    - Mantemos dicionarios de parametros com valores padrao neste arquivo (facil de versionar e reproduzir).
    - Permite sobrescrever os principais parametros via linha de comando (melhor DX para automacao).

Observacao: este arquivo nao altera main2.py. E um wrapper CLI separado para testes.
"""

from __future__ import annotations

import argparse
import logging
import os
import random
from typing import Iterable, List, Tuple

import numpy as np
from funcoes import (
    ler_arquivo_ghe,
    ler_numero_tarefas,
    gera_populacao_inicial,
    salva_populacao,
    carrega_populacao,
    gera_hash,
)
from main2 import (
    salva as salva_main,
    salvar_populacao_csv as salvar_populacao_csv_main,
    carrega as carrega_main,
    experimento as experimento_main,
    salva_resultados as salva_resultados_main,
)


# =============================
# Parametros padrao (edite aqui)
# =============================
# Voce pode editar diretamente estes dicionarios para ajustar os padroes do seu AG.
# Alternativamente, pode sobrescrever via CLI (veja --help ou comando "docs").
DEFAULT_PARAM_POPULACAO = {
    "tamanhoPopulacao": 10,
    "grafo": "grafos_experimento/robot-4-20-30.stg",
}

DEFAULT_PARAM_MSE = {
    "numeroIteracoes": 10,
    "chanceCrossoverAlocacao": 0.4,
    "chanceCrossoverEscalonamento": 0.4,
    "chanceMutacaoAlocacao": 0.2,
    "chanceMutacaoEscalonamento": 0.2,
    "taxaElitismo": 0.2,
    # tamanhoPopulacao é herdado de DEFAULT_PARAM_POPULACAO por padrão
}

DEFAULT_ALPHAS = ["0.5"]  # Edite a lista padrao de alphas se desejar
DEFAULT_PASTA_RESULTADOS = "resultados2"


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def validar_grafo(caminho_grafo: str) -> None:
    if not os.path.exists(caminho_grafo):
        raise FileNotFoundError(f"Grafo nao encontrado: {caminho_grafo}")
    # Verificacao minima do padrao de nome (ex.: robot-4-20-30.stg -> pega '4' como numProcessadores)
    partes = os.path.basename(caminho_grafo).split("-")
    if len(partes) < 2 or not partes[1].isdigit():
        logging.warning(
            "Nao foi possivel inferir numProcessadores pelo nome do arquivo. Verifique o padrao '<nome>-<proc>-...'")


def parse_alphas(alpha_args: Iterable[str] | None) -> List[str]:
    if not alpha_args:
        return list(DEFAULT_ALPHAS)
    final: List[str] = []
    for a in alpha_args:
        # aceita --alpha 0.5 --alpha 0.7 ou --alpha 0.5,0.7
        for part in str(a).split(","):
            part = part.strip()
            if part:
                final.append(part)
    return final


# Removido: funcoes auxiliares duplicadas (gerar_e_salvar_populacao, carregar_populacao_por_hash,
# salva_resultados_cli, experimento_cli). Utilizamos diretamente as funcoes do main2.py.


def comando_salvar(args: argparse.Namespace) -> int:
    if args.seed is not None:
        np.random.seed(args.seed)
        random.seed(args.seed)
        logging.debug(f"Seeds configuradas: {args.seed}")

    grafo = args.grafo or DEFAULT_PARAM_POPULACAO["grafo"]
    validar_grafo(grafo)
    tamanho = args.tamanho_populacao or DEFAULT_PARAM_POPULACAO["tamanhoPopulacao"]

    # Monta parametros e delega para main2.salva
    parametros_pop = {"tamanhoPopulacao": tamanho, "grafo": grafo}
    logging.info("Gerando e salvando populacao...")
    hash_pop = salva_main(parametros_pop)

    # Imprime apenas o hash ao final (facil para scripts)
    print(f"Hash da população: {hash_pop}")
    return 0


def comando_carregar(args: argparse.Namespace) -> int:
    if args.seed is not None:
        np.random.seed(args.seed)
        random.seed(args.seed)
        logging.debug(f"Seeds configuradas: {args.seed}")

    if not args.hash:
        logging.error("--hash e obrigatorio para o comando 'carregar'.")
        return 2

    grafo = args.grafo or DEFAULT_PARAM_POPULACAO["grafo"]
    validar_grafo(grafo)

    # Monta parametros com defaults + overrides (valor de tamanhoPopulacao pode ser ajustado apos carregar a populacao)
    tamanho_pop = (
        args.tamanho_populacao
        if args.tamanho_populacao is not None
        else DEFAULT_PARAM_POPULACAO["tamanhoPopulacao"]
    )

    parametros_mse = dict(DEFAULT_PARAM_MSE)
    parametros_mse["tamanhoPopulacao"] = tamanho_pop
    if args.iteracoes is not None:
        parametros_mse["numeroIteracoes"] = args.iteracoes
    if args.cx_alloc is not None:
        parametros_mse["chanceCrossoverAlocacao"] = args.cx_alloc
    if args.cx_sched is not None:
        parametros_mse["chanceCrossoverEscalonamento"] = args.cx_sched
    if args.mut_alloc is not None:
        parametros_mse["chanceMutacaoAlocacao"] = args.mut_alloc
    if args.mut_sched is not None:
        parametros_mse["chanceMutacaoEscalonamento"] = args.mut_sched
    if args.elitismo is not None:
        parametros_mse["taxaElitismo"] = args.elitismo

    alphas = parse_alphas(args.alpha)
    pasta_resultados = args.pasta_resultados or DEFAULT_PASTA_RESULTADOS

    # Carrega populacao e verifica hash (via main2.carrega)
    logging.info(f"Carregando populacao de hash: {args.hash}")
    populacao = carrega_main(args.hash)
    hash_calculado = gera_hash(populacao)
    if hash_calculado != args.hash:
        logging.error(
            "Hash da populacao nao confere com o conteudo carregado.")
        return 3

    # Se o usuario nao informou --tamanho-populacao, ajusta a partir do PKL carregado
    if args.tamanho_populacao is None:
        tamanho_real = len(populacao)
        parametros_mse["tamanhoPopulacao"] = tamanho_real

    num_tarefas = ler_numero_tarefas(grafo)
    num_processadores = int(os.path.basename(grafo).split("-")[1])
    dic = ler_arquivo_ghe(grafo, num_processadores)

    logging.info(
        "Iniciando experimento | iteracoes=%s | tamanhoPop=%s | alphas=%s | chanceCrossoverAlocacao=%s | chanceCrossoverEscalonamento=%s | chanceMutacaoAlocacao=%s | chanceMutacaoEscalonamento=%s | taxaElitismo=%s",
        parametros_mse["numeroIteracoes"],
        parametros_mse["tamanhoPopulacao"],
        ",".join(alphas),
        parametros_mse["chanceCrossoverAlocacao"],
        parametros_mse["chanceCrossoverEscalonamento"],
        parametros_mse["chanceMutacaoAlocacao"],
        parametros_mse["chanceMutacaoEscalonamento"],
        parametros_mse["taxaElitismo"],
    )

    # Executa experimento via main2.experimento (ele salva resultados e retorna hashes)
    hashes = experimento_main(
        alphas,
        dic,
        parametros_mse,
        num_tarefas,
        populacao,
        args.hash,
        num_processadores,
        pasta_resultados,
        None,
    )

    print("Hashes das últimas iterações:")
    for h in hashes:
        print(h)
    return 0


def comando_salvar_executar(args: argparse.Namespace) -> int:
    # 1) Salvar
    salvar_args = argparse.Namespace(
        grafo=args.grafo,
        tamanho_populacao=args.tamanho_populacao,
        seed=args.seed,
        verbose=args.verbose,
    )
    hash_pop = None
    try:
        # Reutiliza comando_salvar internamente
        tamanho = salvar_args.tamanho_populacao or DEFAULT_PARAM_POPULACAO["tamanhoPopulacao"]
        grafo = salvar_args.grafo or DEFAULT_PARAM_POPULACAO["grafo"]
        validar_grafo(grafo)
        parametros_pop = {"tamanhoPopulacao": tamanho, "grafo": grafo}
        logging.info("Gerando e salvando populacao...")
        hash_pop = salva_main(parametros_pop)
    except Exception:
        logging.exception("Falha ao gerar/salvar populacao inicial")
        return 4

    print(f"Hash da populacao inicial gerada: {hash_pop}")

    # 2) Executar
    carregar_args = argparse.Namespace(
        grafo=args.grafo,
        tamanho_populacao=args.tamanho_populacao,
        seed=args.seed,
        iteracoes=args.iteracoes,
        cx_alloc=args.cx_alloc,
        cx_sched=args.cx_sched,
        mut_alloc=args.mut_alloc,
        mut_sched=args.mut_sched,
        elitismo=args.elitismo,
        alpha=args.alpha,
        pasta_resultados=args.pasta_resultados,
        hash=hash_pop,
        verbose=args.verbose,
    )
    return comando_carregar(carregar_args)


def print_docs() -> None:
    msg = rf"""
Uso (PowerShell):

    # Salvar apenas (gera população e imprime o hash)
    python .\main2_cli.py salvar --grafo grafos_experimento\robot-4-20-30.stg --tamanho-populacao 10

    # Carregar e executar (usa hash salvo anteriormente)
    python .\main2_cli.py carregar --hash <HASH> --grafo grafos_experimento\robot-4-20-30.stg --iteracoes 10 --alpha 0.5,0.7 --tamanho-populacao 10 --cx-alloc 0.4 --cx-sched 0.4 --mut-alloc 0.2 --mut-sched 0.2 --elitismo 0.2

    # Salvar e executar em sequência
    python .\main2_cli.py salvar-executar --grafo grafos_experimento\robot-4-20-30.stg --iteracoes 10 --alpha 0.5,0.7 --tamanho-populacao 10

    # Exemplo com seed para reprodutibilidade (vale para qualquer subcomando)
    python .\main2_cli.py salvar --grafo grafos_experimento\robot-4-20-30.stg --tamanho-populacao 10 --seed 42

Parâmetros do AG (padrões no código):
    - Edite os dicionários DEFAULT_PARAM_POPULACAO e DEFAULT_PARAM_MSE neste arquivo.
    - Alternativamente, sobrescreva via CLI com as opções listadas em '--help'.

Notas:
    - O script verifica a consistência do hash carregado.
    - Resultados (CSVs) são salvos em '{DEFAULT_PASTA_RESULTADOS}/<hash_populacao>/' por padrão.
    - Use --verbose para logs detalhados e --seed para reprodutibilidade.
"""
    print(msg)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "CLI para salvar/carregar populações e rodar experimentos do AG."
        )
    )
    parser.add_argument("--verbose", action="store_true",
                        help="Ativa logs detalhados (DEBUG)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Define seed para numpy e random")

    sub = parser.add_subparsers(dest="command", required=True)

    # salvar
    p_salvar = sub.add_parser(
        "salvar", help="Gera e salva uma populacao; imprime o hash gerado")
    p_salvar.add_argument("--grafo", type=str, default=None,
                          help="Caminho para o grafo .stg")
    p_salvar.add_argument("--tamanho-populacao", type=int,
                          default=None, help="Tamanho da populacao inicial")
    # comuns
    p_salvar.add_argument("--seed", type=int, default=None,
                          help="Define seed para numpy e random")
    p_salvar.add_argument("--verbose", action="store_true",
                          help="Ativa logs detalhados (DEBUG)")
    p_salvar.set_defaults(func=comando_salvar)

    # carregar
    p_carregar = sub.add_parser(
        "carregar",
        help="Carrega populacao por hash e roda o experimento; imprime hashes das ultimas iteracoes",
    )
    p_carregar.add_argument(
        "--hash", type=str, required=True, help="Hash da populacao salva")
    p_carregar.add_argument("--grafo", type=str,
                            default=None, help="Caminho para o grafo .stg")
    p_carregar.add_argument("--tamanho-populacao", type=int,
                            default=None, help="Tamanho da populacao para o experimento")
    p_carregar.add_argument("--iteracoes", type=int,
                            default=None, help="Número de iterações")
    p_carregar.add_argument("--alpha", action="append",
                            help="Alpha(s). Pode repetir a opcao ou usar CSV: 0.5,0.7")
    p_carregar.add_argument("--cx-alloc", type=float,
                            default=None, help="Chance de crossover de alocacao")
    p_carregar.add_argument("--cx-sched", type=float, default=None,
                            help="Chance de crossover de escalonamento")
    p_carregar.add_argument("--mut-alloc", type=float,
                            default=None, help="Chance de mutacao de alocacao")
    p_carregar.add_argument("--mut-sched", type=float,
                            default=None, help="Chance de mutacao de escalonamento")
    p_carregar.add_argument("--elitismo", type=float,
                            default=None, help="Taxa de elitismo")
    p_carregar.add_argument("--pasta-resultados", type=str,
                            default=None, help="Diretorio onde salvar CSVs de resultados")
    # comuns
    p_carregar.add_argument("--seed", type=int, default=None,
                            help="Define seed para numpy e random")
    p_carregar.add_argument("--verbose", action="store_true",
                            help="Ativa logs detalhados (DEBUG)")
    p_carregar.set_defaults(func=comando_carregar)

    # salvar-executar
    p_both = sub.add_parser(
        "salvar-executar",
        help="Gera e salva uma populacao e, em seguida, executa o experimento com ela",
    )
    p_both.add_argument("--grafo", type=str, default=None,
                        help="Caminho para o grafo .stg")
    p_both.add_argument("--tamanho-populacao", type=int, default=None,
                        help="Tamanho da populacao inicial e do experimento")
    p_both.add_argument("--iteracoes", type=int,
                        default=None, help="Numero de iteracoes")
    p_both.add_argument("--alpha", action="append",
                        help="Alpha(s). Pode repetir a opcao ou usar CSV: 0.5,0.7")
    p_both.add_argument("--cx-alloc", type=float, default=None,
                        help="Chance de crossover de alocacao")
    p_both.add_argument("--cx-sched", type=float, default=None,
                        help="Chance de crossover de escalonamento")
    p_both.add_argument("--mut-alloc", type=float, default=None,
                        help="Chance de mutacao de alocacao")
    p_both.add_argument("--mut-sched", type=float, default=None,
                        help="Chance de mutacao de escalonamento")
    p_both.add_argument("--elitismo", type=float,
                        default=None, help="Taxa de elitismo")
    p_both.add_argument("--pasta-resultados", type=str, default=None,
                        help="Diretorio onde salvar CSVs de resultados")
    # comuns
    p_both.add_argument("--seed", type=int, default=None,
                        help="Define seed para numpy e random")
    p_both.add_argument("--verbose", action="store_true",
                        help="Ativa logs detalhados (DEBUG)")
    p_both.set_defaults(func=comando_salvar_executar)

    # docs
    p_docs = sub.add_parser(
        "docs", help="Exibe documentacao rapida e exemplos de uso")
    # comuns
    p_docs.add_argument("--verbose", action="store_true",
                        help="Ativa logs detalhados (DEBUG)")
    p_docs.add_argument("--seed", type=int, default=None,
                        help="Define seed para numpy e random")
    p_docs.set_defaults(func=lambda _args: (print_docs(), 0)[1])

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)

    try:
        return args.func(args)
    except FileNotFoundError as e:
        logging.error(str(e))
        return 1
    except KeyboardInterrupt:
        logging.warning("Execucao interrompida pelo usuario")
        return 130
    except SystemExit as e:
        # Deixa argparse propagar saídas adequadas
        return int(getattr(e, "code", 1) or 0)
    except Exception:
        logging.exception("Erro inesperado")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
