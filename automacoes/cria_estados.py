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
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Amazonas"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SP", "São Paulo"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
        ("EX", "Estrangeiro"),
    ]

    for sigla, nome in estados:
        estado, created = Estado.objects.get_or_create(sigla=sigla, nome=nome)
        if created:
            print(f"Estado Criado: {nome} ({sigla})")
        else:
            print(f"Estado Já Existente: {nome} ({sigla})")
