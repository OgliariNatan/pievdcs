# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from sistema_justica.forms.cadastro_mpu import CadastroMedidaProtetiva
from MAIN.decoradores.calcula_tempo import calcula_tempo




@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública',])
def defensoria_publica(request):
    contexto = {
        'title': 'Defensoria Pública',
        'description': 'This page provides information about the public defender service.',
        'encaminhamentos': 2,
        'notificacoes': 2,
        'user': request.user,
    }
    return render(request, "defensoria_publica.html", contexto)

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