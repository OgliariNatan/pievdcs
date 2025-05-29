# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from ..forms.cadastros import CadastroVitimaForm


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


def cadastro_vitima_form(request):
    form = CadastroVitimaForm()
    return render(request, 'parcial/cadastro_vitima_form.html', {'form': form})

def cadastro_vitima_submit(request):
    if request.method == 'POST':
        form = CadastroVitimaForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('<div class="alert alert-success">Vítima cadastrada com sucesso!</div>')
    else:
        return render(request, "parcial/cadastro_vitima_form.html", {"form": form})
    return HttpResponse(status=405)