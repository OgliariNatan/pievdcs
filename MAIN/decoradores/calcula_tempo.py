"""
    Decorador para calcular o tempo de execução de uma função.
"""
import time

def calcula_tempo(funcao):
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = funcao(*args, **kwargs)
        fim = time.time()
        print(f"Tempo de execução do {funcao.__name__}: {fim - inicio:.4f} segundos")
        return resultado
    return wrapper