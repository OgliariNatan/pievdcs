from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['CRAS',])
def cras(request):
    contexto = {
        'title': 'Centros de Referência de Assistência Social',
        'description': 'This page provides information about the CRAS system.',
        'notificacao': 1,
        'encaminhamentos': 1,
        'user' : request.user,
    }
    return render(request, "cras.html", contexto)