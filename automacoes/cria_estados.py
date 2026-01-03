# -*- coding: utf-8 -*-
"""Script para criar estados no banco de dados do sistema de justiça

    Para uso em ambiente de desenvolvimento ou para inicializar o banco de dados com os estados brasileiros.

    @comando:
      python manage.py shell
      from automacoes.cria_estados import *
      >>> criar_estados()
"""


from sistema_justica.models import Estado

def criar_estados():
    estados = [
        ("AC", "Acre", 12),
        ("AL", "Alagoas", 27),
        ("AP", "Amapá", 16),
        ("AM", "Amazonas", 13),
        ("BA", "Bahia", 29),
        ("CE", "Ceará", 23),
        ("DF", "Distrito Federal", 53),
        ("ES", "Espírito Santo", 32),
        ("GO", "Goiás", 52),
        ("MA", "Maranhão", 21),
        ("MT", "Mato Grosso", 51),
        ("MS", "Mato Grosso do Sul", 50),
        ("MG", "Minas Gerais", 31),
        ("PA", "Pará", 15),
        ("PB", "Paraíba", 25),
        ("PR", "Paraná", 41),
        ("PE", "Pernambuco", 26),
        ("PI", "Piauí", 22),
        ("RJ", "Rio de Janeiro", 33),
        ("RN", "Rio Grande do Norte", 24),
        ("RS", "Rio Grande do Sul", 43),
        ("RO", "Rondônia", 11),
        ("RR", "Roraima", 14),
        ("SC", "Santa Catarina", 42),
        ("SP", "São Paulo", 35),
        ("SE", "Sergipe", 28),
        ("TO", "Tocantins", 17),
        ("EX", "Estrangeiro", None),
    ]

    for sigla, nome, codigo in estados:
        estado, created = Estado.objects.get_or_create(sigla=sigla, nome=nome, codigo=codigo)
        if created:
            print(f"Estado Criado: {nome} ({sigla})")
        else:
            print(f"Estado Já Existente: {nome} ({sigla})")
