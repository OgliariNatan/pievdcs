from django.shortcuts import render

def caps(request):
    contexto = {
        'title': 'Centros de Atenção Psicossocial',
        'description': 'This page provides information about the CAPS system.'
    }
    return render(request, "caps.html", contexto)