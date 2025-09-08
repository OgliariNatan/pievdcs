# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from mensageria.models import Notificacao, StatusNotificacaoUsuario, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from sistema_justica.forms.cadastro_mpu import CadastroMedidaProtetiva
from usuarios.models import CustomUser
from MAIN.decoradores.calcula_tempo import calcula_tempo



@calcula_tempo
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública',])
def defensoria_publica(request):

    #contar notificações não lidas
    notificacoes_nao_lidas = StatusNotificacaoUsuario.objects.filter(
        usuario=request.user,
        status=StatusNotificacao.NAO_LIDA
    ).count()

    # Encaminhamentos mensais 
    encaminhamentos_mensais = 0

    contexto = {
        'title': 'Defensoria Pública',
        'description': 'This page provides information about the public defender service.',
        'encaminhamentos': encaminhamentos_mensais,
        'notificacoes': notificacoes_nao_lidas,
        'user': request.user,
    }
    return render(request, "defensoria_publica.html", contexto)

@calcula_tempo
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública',])
def listar_encaminhamentos(request):
    """ Lista de encaminhamentos da defensoria pública """
    #encaminhamentos = Notificacao.objects.filter(prioridade='ALTA', usuario=request.user)
    encaminhamentos_all = Notificacao.objects.filter(destinatario_usuario=request.user)
    encaminhamentos = encaminhamentos_all.order_by('-data_criacao')[:10]  # Últimos 10 encaminhamentos
    encaminhamentos = dict(encaminhamentos)
    
    context = {
        'title': 'Encaminhamentos - Defensoria Pública',
        'description': 'This page lists all referrals made by the public defender service.',
        'encaminhamentos': encaminhamentos,
    }
    return render(request, "encaminhamentos.html", context)




@calcula_tempo
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública', 'Ministério Público',])
def cadastro_mpu(request):
    mensagem_sucesso = None
    if request.method == "POST":
        form = CadastroMedidaProtetiva(request.POST)
        if form.is_valid():
            form.save()
            mensagem_sucesso = "Medida Protetiva cadastrada com sucesso!"
            form = CadastroMedidaProtetiva()  # Limpa o formulário após sucesso
    else:
        form = CadastroMedidaProtetiva()
    contexto = {
        'form': form,
        'mensagem_sucesso': mensagem_sucesso,
    }
    return render(request, "parcial/cadastro_mpu.html", contexto)

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública', 'Ministério Público',])
def consulta_mpu(request):
    # Implementar a lógica de consulta de MPU aqui
    contexto = {
        'title': 'Consulta MPU',
        'description': 'This page allows you to consult existing MPU records.',
    }
    return render(request, "parcial/consulta_mpu.html", contexto)