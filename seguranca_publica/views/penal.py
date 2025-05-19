from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def penal(request):
    contexto = {
        'title': 'Policia Penal',
        'description': 'This page provides information about the penal system.',
        'encaminhamentos': 5,
        'alert': 2,
        'user' : request.user,
    }
    return render(request, "penal.html", contexto)