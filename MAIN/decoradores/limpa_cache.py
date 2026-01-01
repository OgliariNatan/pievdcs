# -*- coding: utf-8 -*-
"""
Módulo de utilitários para gerenciamento de cache Redis no PIEVDCS.
Path: MAIN/decoradores/limpa_cache.py

Autor: OgliariNatan
Data: 2025
"""

from django.core.cache import cache
import os
from dotenv import load_dotenv

load_dotenv()
var_debug = os.getenv('DEBUG', 'False')


def obter_todas_chaves_cache(padrao='pievdcs:*'):
    """
    Obtém TODAS as chaves do cache Redis.
    
    Equivalente ao hipotético cache.all() que não existe.
    
    Args:
        padrao (str): Padrão de busca. Padrão: 'pievdcs:*' (todas do PIEVDCS)
        
    Returns:
        dict: Dicionário com {chave: valor} de todas as chaves encontradas
        
    Exemplo:
        >>> todas = obter_todas_chaves_cache()
        >>> print(todas)
        {
            'pievdcs:1:tipos_violencia_ativos': [{'id': 1, 'nome': 'Física'}, ...],
            'pievdcs:1:dashboard_stats': {'total': 150, ...},
            ...
        }
    """
    try:
        # Acessar cliente Redis diretamente
        cliente_redis = cache._cache.get_client()
        
        # Buscar todas as chaves com padrão
        chaves_raw = cliente_redis.keys(padrao)
        
        # Converter bytes para string e obter valores
        resultado = {}
        
        for chave_raw in chaves_raw:
            # Decodificar chave
            chave = chave_raw.decode('utf-8') if isinstance(chave_raw, bytes) else chave_raw
            
            # Remover prefixo do django-redis para usar com cache.get()
            # Ex: 'pievdcs:1:tipos_violencia' → 'tipos_violencia'
            if ':' in chave:
                partes = chave.split(':', 2)
                chave_limpa = partes[-1] if len(partes) >= 3 else chave
            else:
                chave_limpa = chave
            
            # Obter valor
            valor = cache.get(chave_limpa)
            
            if valor is not None:
                resultado[chave] = valor
        
        if var_debug == 'True':
            print(f"✅ {len(resultado)} entradas de cache recuperadas")
        
        return resultado
    
    except Exception as e:
        if var_debug == 'True':
            print(f"⚠️  Erro ao obter todas as chaves: {e}")
        return {}


def listar_chaves_cache(padrao='pievdcs:*'):
    """
    Lista apenas os NOMES das chaves sem carregar valores.
    Mais rápido que obter_todas_chaves_cache().
    
    Args:
        padrao (str): Padrão de busca. Padrão: 'pievdcs:*'
        
    Returns:
        list: Lista de nomes de chaves
        
    Exemplo:
        >>> chaves = listar_chaves_cache()
        >>> print(chaves)
        ['pievdcs:1:tipos_violencia_ativos', 'pievdcs:1:dashboard_stats']
    """
    try:
        cliente_redis = cache._cache.get_client()
        chaves_raw = cliente_redis.keys(padrao)
        
        chaves = [
            chave.decode('utf-8') if isinstance(chave, bytes) else chave
            for chave in chaves_raw
        ]
        
        if var_debug == 'True':
            print(f"✅ {len(chaves)} chaves encontradas no cache")
        
        return chaves
    
    except Exception as e:
        if var_debug == 'True':
            print(f"⚠️  Erro ao listar chaves: {e}")
        return []


def obter_resumo_cache():
    """
    Obtém resumo do cache com estatísticas e exemplos.
    Alternativa performática ao cache.all().
    
    Returns:
        dict: Resumo completo do cache
        
    Exemplo:
        >>> resumo = obter_resumo_cache()
        >>> print(resumo)
        {
            'total_chaves': 5,
            'chaves_por_prefixo': {'pievdcs': 3, 'outro': 2},
            'exemplos': ['pievdcs:1:tipos_violencia_ativos', ...],
            'memoria_mb': 2.5
        }
    """
    try:
        cliente_redis = cache._cache.get_client()
        
        # Obter todas as chaves
        todas_chaves = cliente_redis.keys('*')
        total = len(todas_chaves)
        
        # Agrupar por prefixo
        chaves_por_prefixo = {}
        for chave_raw in todas_chaves:
            chave = chave_raw.decode('utf-8') if isinstance(chave_raw, bytes) else chave_raw
            prefixo = chave.split(':')[0] if ':' in chave else 'sem_prefixo'
            chaves_por_prefixo[prefixo] = chaves_por_prefixo.get(prefixo, 0) + 1
        
        # Informações de memória
        info = cliente_redis.info('memory')
        memoria_bytes = info.get('used_memory', 0)
        memoria_mb = round(memoria_bytes / (1024 * 1024), 2)
        
        # Exemplos de chaves (primeiras 10)
        exemplos = [
            chave.decode('utf-8') if isinstance(chave, bytes) else chave
            for chave in list(todas_chaves)[:10]
        ]
        
        resumo = {
            'total_chaves': total,
            'chaves_por_prefixo': chaves_por_prefixo,
            'exemplos': exemplos,
            'memoria_mb': memoria_mb,
            'redis_version': info.get('redis_version', 'N/A')
        }
        
        if var_debug == 'True':
            print(f"✅ Resumo do cache gerado:")
            print(f"   - Total: {total} chaves")
            print(f"   - Memória: {memoria_mb} MB")
            print(f"   - Prefixos: {list(chaves_por_prefixo.keys())}")
        
        return resumo
    
    except Exception as e:
        if var_debug == 'True':
            print(f"⚠️  Erro ao gerar resumo: {e}")
        return {
            'total_chaves': 0,
            'erro': str(e)
        }


def iterar_cache(padrao='pievdcs:*', limite=None):
    """
    Itera sobre entradas do cache de forma eficiente.
    Útil para processar grandes quantidades sem carregar tudo na memória.
    
    Args:
        padrao (str): Padrão de busca. Padrão: 'pievdcs:*'
        limite (int, optional): Limite de chaves a processar. None = todas
        
    Yields:
        tuple: (chave, valor) para cada entrada
        
    Exemplo:
        >>> for chave, valor in iterar_cache('pievdcs:*', limite=5):
        >>>     print(f"{chave}: {valor}")
        pievdcs:1:tipos_violencia_ativos: [{'id': 1, ...}]
        pievdcs:1:dashboard_stats: {'total': 150}
    """
    try:
        cliente_redis = cache._cache.get_client()
        chaves_raw = cliente_redis.keys(padrao)
        
        processadas = 0
        
        for chave_raw in chaves_raw:
            if limite and processadas >= limite:
                break
            
            # Decodificar chave
            chave = chave_raw.decode('utf-8') if isinstance(chave_raw, bytes) else chave_raw
            
            # Remover prefixo django-redis
            if ':' in chave:
                partes = chave.split(':', 2)
                chave_limpa = partes[-1] if len(partes) >= 3 else chave
            else:
                chave_limpa = chave
            
            # Obter valor
            valor = cache.get(chave_limpa)
            
            if valor is not None:
                yield (chave, valor)
                processadas += 1
        
        if var_debug == 'True':
            print(f"✅ {processadas} entradas iteradas")
    
    except Exception as e:
        if var_debug == 'True':
            print(f"⚠️  Erro ao iterar cache: {e}")


# ========================================================================
# EXEMPLOS DE USO
# ========================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ALTERNATIVAS AO cache.all() NO PIEVDCS")
    print("="*60 + "\n")
    
    # 1. Listar apenas chaves (rápido)
    print("1️⃣  Listar chaves (rápido):")
    chaves = listar_chaves_cache('pievdcs:*')
    print(f"   Total: {len(chaves)} chaves")
    for chave in chaves[:3]:
        print(f"   - {chave}")
    
    # 2. Obter resumo (médio)
    print("\n2️⃣  Resumo do cache:")
    resumo = obter_resumo_cache()
    print(f"   Total: {resumo['total_chaves']} chaves")
    print(f"   Memória: {resumo['memoria_mb']} MB")
    
    # 3. Obter todas chaves e valores (lento)
    print("\n3️⃣  Todas as chaves com valores:")
    todas = obter_todas_chaves_cache('pievdcs:*')
    print(f"   Total: {len(todas)} entradas")
    
    # 4. Iterar de forma eficiente
    print("\n4️⃣  Iterar primeiras 3 entradas:")
    for idx, (chave, valor) in enumerate(iterar_cache('pievdcs:*', limite=3), 1):
        tipo_valor = type(valor).__name__
        print(f"   {idx}. {chave} → {tipo_valor}")
    
    print("\n" + "="*60 + "\n")