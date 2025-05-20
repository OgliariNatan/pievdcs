from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['CREAS'])

def creas(request):
    contexto = {
        'title': 'CREAS',
        'description': 'This page provides information about the CREAS system.',
        'encaminhamentos': 2,  # Criar variaveis para encaminhamentos
        'notificacao': 1,
        'user' : request.user,
    }
    return render(request, "creas.html", contexto)