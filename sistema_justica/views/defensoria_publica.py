# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos




@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Defensoria Pública'])
def defensoria_publica(request):
    contexto = {
        'title': 'Defensoria Pública',
        'description': 'This page provides information about the public defender service.',
        'encaminhamentos': 2,
        'notificacoes': 2,
        'user': request.user,
    }
    return render(request, "defensoria_publica.html", contexto)