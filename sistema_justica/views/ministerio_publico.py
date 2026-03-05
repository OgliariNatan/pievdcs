from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
from .permission_group import grupos_permitidos
from mensageria.models import Notificacao

from datetime import date, timedelta


ANO_CORRENTE = date.today().year

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Ministério Público',])
def ministerio_publico(request):
    notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)
    encaminhamentos_nao_lidos = Notificacao.contar_encaminhamentos_nao_lidos(request.user)

    contexto = {
        'title': 'Ministério Público',
        'description': 'Página do Ministério Público - Sistema PIEVDCS',
        'ano_corrente': ANO_CORRENTE,
        'encaminhamentos': encaminhamentos_nao_lidos,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'user': request.user,
    }
    return render(request, "ministerio_publico.html", contexto)