from django.shortcuts import render

def cientifica(request):
    contexto = {
        'title': 'Polícia Cientifica',
        'description': 'This page provides information about the cientifica system.'
    }
    return render(request, "cientifica.html", contexto)