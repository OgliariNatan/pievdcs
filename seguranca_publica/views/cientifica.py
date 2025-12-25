from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy 
from .permission_group import grupos_permitidos
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from usuarios.models import CustomUser
from django.contrib.auth.models import Group


""" Configuraçao de decoradores para debug """
import os
from dotenv import load_dotenv

var_debug = os.getenv('DEBUG', False) #Carrega apenas a variavel de debug

if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
    
else:
    checked_debug_decorador = None
    checked_debug_decorador_fun = None

""" Fim da configuraçao de decoradores para debug """


@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Científica'])       
def cientifica(request):

    notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)

    contexto = {
        'title': 'Polícia Cientifica',
        'encaminhamentos': 5,
        'alert': notificacoes_nao_lidas,
        'description': 'This page provides information about the cientifica system.',
        'user' : request.user,
    }
    return render(request, "cientifica.html", contexto)