from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from usuarios.models import CustomUser
from django.contrib.auth.models import Group as CustomGroup
from datetime import datetime

""" Configuraçao de decoradores para debug """
import os
from dotenv import load_dotenv

var_debug = os.getenv('DEBUG', False) #Carrega apenas a variavel de debug

if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
    
else:
    checked_debug_decorador = lambda x: x
    checked_debug_decorador_fun = lambda x: x

""" Fim da configuraçao de decoradores para debug """


def ANO_CORRENETE():
    return datetime.now().year

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Civil'])
@checked_debug_decorador
def civil(request):
    try:
        notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)
    except Notificacao.DoesNotExist:
        notificacoes_nao_lidas = 0
    try:    
        encaminhamentos_nao_lidos = Notificacao.contar_encaminhamentos_nao_lidos(request.user)
    except Notificacao.DoesNotExist:
        encaminhamentos_nao_lidos = 0

    contexto = {
        'title': 'Polícia Civil',
        'encaminhamentos_nao_lidos': encaminhamentos_nao_lidos,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'description': 'Pagina destinada a Polícia Civil.',
        'user' : request.user,
        'ano_corrente': ANO_CORRENETE(),
    }
    return render(request, "civil.html", contexto)
