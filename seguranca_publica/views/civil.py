from django.shortcuts import render

def civil(request):
    contexto = {
        'title': 'Polícia civil',
        'encaminhamentos': 5,
        'alert': 2,
        'description': 'This page provides information about the civil system.'
    }
    return render(request, "civil.html", contexto)