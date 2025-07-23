from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy 
from .permission_group import grupos_permitidos

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Científica'])       
def cientifica(request):
    contexto = {
        'title': 'Polícia Cientifica',
        'encaminhamentos': 5,
        'alert': 2,
        'description': 'This page provides information about the cientifica system.',
        'user' : request.user,
    }
    return render(request, "cientifica.html", contexto)