from django.shortcuts import render

def militar(request):
    contexto = {
        'title': 'Polícia Militar',
        'encaminhamentos': 5,
        'alert': 2,
        'description': 'This page provides information about the militar system.'
    }
    return render(request, "militar.html", contexto)