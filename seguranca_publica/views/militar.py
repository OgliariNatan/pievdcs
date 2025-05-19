from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

@login_required(login_url=reverse_lazy('login'))
def militar(request):
    contexto = {
        'title': 'Polícia Militar',
        'encaminhamentos': 5,
        'alert': 2,
        'description': 'This page provides information about the militar system.',
        'user' : request.user,
    }
    return render(request, "militar.html", contexto)