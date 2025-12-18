# -*- coding: utf-8 -*-
""" 
    Para criacao de base de dados ficticios para testes e validacoes
    @autor: ogliari
    @update: 20251218
    @comando:
      python manage.py shell < automacoes/inserir_dados.py
"""


from automacoes.cria_estados import *
from automacoes.atribui_municipio import *

"""Cria estados no db"""
criar_estados()
"""Atribui todos os municipios aos estados no db"""
cadastrar_municipios_por_estado()