from django.shortcuts import render

def poder_judiciario(request):
    contexto = {
        'title': 'Poder Judiciário',
        'description': 'This page provides information about the judicial power.',
        'encaminhamentos': 5,
        'notificacoes': 4,
    }
    return render(request, "poder_judiciario.html", contexto)