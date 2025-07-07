from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Conselho Tutelar',])
def conselho_tutelar(request):
    contexto = {
        'title': 'Conselho Tutelar',
        'description': 'This page provides information about the conselho tutelar system.',
        'encaminhamentos': 1,  # Criar variaveis para encaminhamentos
        'notificacao': 1,
        'user' : request.user,
    }
    return render(request, "conselho_tutelar.html", contexto)