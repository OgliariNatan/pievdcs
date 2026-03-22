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
]