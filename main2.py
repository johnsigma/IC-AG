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
    carrega_populacao
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
        populacao = gera_populacao_inicial(dic, numTarefas, numProcessadores, tamanhoPopulacao)
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
    
    
def main():
    parametros = {
        "tamanhoPopulacao": 10,
        "grafo": "grafos_experimento/robot-4-20-30.stg",
        "hashPopulacao": "c1b8c7a8-8f0b-4b4e-8d6b-4f4c1c7b4e8d"
    }
    
    hashPopulacao = salva(parametros)
    populacao = carrega(hashPopulacao)
    for i in range(len(populacao)):
        individuo = populacao[i]
        print(f'Individuo {i}')
        print(f'Makespan: {individuo['makespan']}')
        print(f'Fitness: {individuo['fitness']}')
    
if __name__ == "__main__":
    main()