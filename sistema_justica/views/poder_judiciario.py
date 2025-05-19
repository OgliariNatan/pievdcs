from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from ..views.permission_group import grupos_permitidos

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário'])
def poder_judiciario(request):
    contexto = {
        'title': 'Poder Judiciário',
        'description': 'This page provides information about the judicial power.',
        'encaminhamentos': 5,
        'notificacoes': 4,
        'user': request.user,
    }
    return render(request, "poder_judiciario.html", contexto)