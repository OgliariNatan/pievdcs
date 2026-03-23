# -*- coding: utf-8 -*-
"""
dir: usuarios/urls.py
Rotas do app de usuários.
"""
from django.urls import path

from .views import (
    config_conta,
    config_conta_arquivos_popup,
    config_conta_arquivos_submit,
    config_conta_dados_popup,
    config_conta_dados_submit,
    config_conta_senha_popup,
    config_conta_senha_submit,
    config_conta_gestao,
    config_conta_gestao_buscar,
    config_conta_gestao_adicionar,
    config_conta_gestao_remover,
    config_conta_gestao_criar_popup,
    config_conta_gestao_criar_submit,
)

app_name = 'usuarios'

urlpatterns = [
    path('config-conta/', config_conta, name='config_conta'),
    path('config-conta/dados/', config_conta_dados_popup, name='config_conta_dados_popup'),
    path('config-conta/dados/salvar/', config_conta_dados_submit, name='config_conta_dados_submit'),
    path('config-conta/senha/', config_conta_senha_popup, name='config_conta_senha_popup'),
    path('config-conta/senha/salvar/', config_conta_senha_submit, name='config_conta_senha_submit'),
    path('config-conta/arquivos/', config_conta_arquivos_popup, name='config_conta_arquivos_popup'),
    path('config-conta/arquivos/salvar/', config_conta_arquivos_submit, name='config_conta_arquivos_submit'),
    path('config-conta/gestao/', config_conta_gestao, name='config_conta_gestao'),
    path('config-conta/gestao/buscar/', config_conta_gestao_buscar, name='config_conta_gestao_buscar'),
    path('config-conta/gestao/adicionar/', config_conta_gestao_adicionar, name='config_conta_gestao_adicionar'),
    path('config-conta/gestao/remover/', config_conta_gestao_remover, name='config_conta_gestao_remover'),
    path('config-conta/gestao/criar/', config_conta_gestao_criar_popup, name='config_conta_gestao_criar_popup'),
    path('config-conta/gestao/criar/salvar/', config_conta_gestao_criar_submit, name='config_conta_gestao_criar_submit'),
]