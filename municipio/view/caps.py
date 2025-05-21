from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['CAPS'])
def caps(request):
    contexto = {
        'title': 'Centros de Atenção Psicossocial',
        'description': 'This page provides information about the CAPS system.',
        'notificacao': 3,
        'encaminhamentos': 2,
        'user' : request.user,
    }
    return render(request, "caps.html", contexto)