"""
    Decorador para calcular o tempo de execução de uma função & o IP do acesso.
"""
import time
import socket
import uuid
from functools import wraps
from django.db import connection

def calcula_tempo(funcao):
    @wraps(funcao)
    def wrapper(request, *args, **kwargs):
        
        
        # Captura o IP real do cliente considerando proxies reversos
        ip_cliente = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_cliente:
            # Em caso de múltiplos proxies, pega o primeiro IP
            ip_cliente = ip_cliente.split(',')[0].strip()
        else:
            # Fallback para REMOTE_ADDR se não houver proxy
            ip_cliente = request.META.get('REMOTE_ADDR', 'IP não disponível')
        
        # Captura informações do servidor (para debug)
        ip_servidor = socket.gethostbyname(socket.gethostname())
        hostname_servidor = socket.gethostname()
        inicio = time.time()
        resultado = funcao(request, *args, **kwargs)
        fim = time.time()
        
        print('----------------------------------------')
        print(f'Tempo: {time.strftime("%d-%m-%Y %H:%M:%S")}')
        print(f'\033[34mIP do cliente:\033[0m \033[33m{ip_cliente}\033[0m')
        #print(f'IP do servidor: {ip_servidor}\tHostname: {hostname_servidor}\tMAC: {uuid.getnode()}')
        print(f"\033[31mTempo de execução do {funcao.__name__}: {fim - inicio:.4f} segundos\033[0m")
        print(f'\033[34mNúmero de queries executadas:\033[0m \033[31m{len(connection.queries)}\033[0m')
        print('----------------------------------------')
        
        return resultado
    return wrapper

def calcula_tempo_fun(funcao):
    """
    Decorador simplificado para calcular tempo de funções auxiliares
    que NÃO recebem o objeto 'request'.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        
        # Executa a função original
        resultado = funcao(*args, **kwargs)
        
        fim = time.time()

        print('\n'*4)
        print('---------- FUNÇÃO AUXILIAR -----------')
        print(f'Tempo: {time.strftime("%d-%m-%Y %H:%M:%S")}')
        print(f"\033[31mExecução de '{funcao.__name__}': {fim - inicio:.4f} segundos\033[0m")
        print(f'\033[34mNúmero de queries executadas:\033[0m \033[31m{len(connection.queries)}\033[0m')
        print('--------------------------------------')
        
        return resultado
    return wrapper