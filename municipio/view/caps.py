from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from usuarios.models import CustomUser
from MAIN.decoradores.calcula_tempo import calcula_tempo

#@permission_required('CAPS.view_caps', login_url=reverse_lazy('login'))
@calcula_tempo
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['CAPS',])
def caps(request):
    notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)
    contexto = {
        'title': 'Centros de Atenção Psicossocial',
        'description': 'This page provides information about the CAPS system.',
        'notificacao': notificacoes_nao_lidas,
        'encaminhamentos': 2,
        'user' : request.user,
    }
    return render(request, "caps.html", contexto)
