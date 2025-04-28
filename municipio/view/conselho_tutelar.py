from django.shortcuts import render

def conselho_tutelar(request):
    contexto = {
        'title': 'Conselho Tutelar',
        'description': 'This page provides information about the conselho tutelar system.'
    }
    return render(request, "conselho_tutelar.html", contexto)