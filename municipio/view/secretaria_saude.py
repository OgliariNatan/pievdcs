from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from usuarios.models import CustomUser, CustomGroup
from MAIN.decoradores.calcula_tempo import calcula_tempo


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Secretaria da Saúde',])
@calcula_tempo
def secretaria_saude(request):
    notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)
    contexto = {
        'title': 'Secretaria de Saúde',
        'description': 'This page provides information about the Secretaria de Saúde system.',
        'encaminhamentos': 2,  # Criar variaveis para encaminhamentos
        'notificacao': notificacoes_nao_lidas,
        'user' : request.user,
    }
    return render(request, "secretaria_saude.html", contexto)