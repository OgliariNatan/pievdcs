from django.shortcuts import render

def civil(request):
    contexto = {
        'title': 'Polícia civil',
        'description': 'This page provides information about the civil system.'
    }
    return render(request, "civil.html", contexto)