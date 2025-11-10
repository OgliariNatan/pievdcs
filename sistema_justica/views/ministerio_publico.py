from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden

from .permission_group import grupos_permitidos


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Ministério Público',])
def ministerio_publico(request):
    contexto = {
        'title': 'Ministério Público',
        'description': 'This page provides information about the public ministry.',
        'encaminhamentos': 5,
        'notificacoes': 2,
        'user': request.user,
    }
    return render(request, "ministerio_publico.html", contexto)