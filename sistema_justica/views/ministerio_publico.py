from django.shortcuts import render

def ministerio_publico(request):
    contexto = {
        'title': 'Ministério Público',
        'description': 'This page provides information about the public ministry.',
        'encaminhamentos': 5,
        'notificacoes': 2,
    }
    return render(request, "ministerio_publico.html", contexto)