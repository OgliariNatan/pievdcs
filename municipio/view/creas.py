from django.shortcuts import render

def creas(request):
    contexto = {
        'title': 'CREAS',
        'description': 'This page provides information about the CREAS system.'
    }
    return render(request, "creas.html", contexto)