# -*- coding: utf-8 -*-
""" 
    Para criacao de base de dados ficticios para testes e validacoes
    @autor: ogliari
    @update: 20251218
    @Obs:
    ---- Deverá seguir a ordem dos scripts de automacoes ----
    @comando:
      python manage.py shell < automacoes/inserir_dados.py
"""


from automacoes.cria_estados import *
from automacoes.atribui_municipio import *
from automacoes.cria_comarcas import cadastrar_comarcas_judiciario_sc
from automacoes.gera_vitimas import criar_vitimas_aleatorias
from automacoes.gera_agressores import criar_agressores_aleatorios
from automacoes.gera_formularios_mp import criar_formularios_mp_aleatorios
from automacoes.cria_grupos import criar_grupos_institucionais



#Cria estados no db
criar_estados()

#Atribui todos os municipios aos estados no db
cadastrar_municipios_por_estado()

#Atribui todas as comarcas do judiciario de SC no db
cadastrar_comarcas_judiciario_sc()

#Cria grupos institucionais no db
criar_grupos_institucionais()

#Cria 3500 vitimas aleatorias no db
criar_vitimas_aleatorias(3500)

#Cria 2500 agressores aleatorios no db
criar_agressores_aleatorios(2500)

#Cria 5000 formularios de medida protetiva aleatorios no db
criar_formularios_mp_aleatorios(5000)

print('\n'*5)
print("="*40)
print("Inserção de dados concluída!")
print("="*50)
print('\n'*5)