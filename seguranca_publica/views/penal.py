from django.shortcuts import render

def penal(request):
    contexto = {
        'title': 'Policia Penal',
        'description': 'This page provides information about the penal system.',
        'encaminhamentos': 5,
        'alert': 2,
        'user' : request.user,
    }
    return render(request, "penal.html", contexto)