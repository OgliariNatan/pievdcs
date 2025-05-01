from django.shortcuts import render

def cras(request):
    contexto = {
        'title': 'Centros de Referência de Assistência Social',
        'description': 'This page provides information about the CRAAS system.'
    }
    return render(request, "cras.html", contexto)