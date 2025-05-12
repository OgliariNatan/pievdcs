from django.shortcuts import render

def defensoria_publica(request):
    contexto = {
        'title': 'Defensoria Pública',
        'description': 'This page provides information about the public defender service.',
        'encaminhamentos': 2,
        'notificacoes': 2,
    }
    return render(request, "defensoria_publica.html", contexto)