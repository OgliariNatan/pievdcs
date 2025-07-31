"""
    Decorador para calcular o tempo de execução de uma função & o IP do acesso.
"""
import time
import socket
import uuid

def calcula_tempo(funcao):
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = funcao(*args, **kwargs)
        fim = time.time()
        print('----------------------------------------')
        print(f'IP do acesso: {socket.gethostbyname(socket.gethostname())}\t{socket.gethostname()}\tMAC: {uuid.getnode()}')
        print(f"Tempo de execução do {funcao.__name__}: {fim - inicio:.4f} segundos")
        #print(f'Endereço MAC: {uuid.getnode()}')
        return resultado
    return wrapper 