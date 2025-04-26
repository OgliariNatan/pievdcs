from django.shortcuts import render

def militar(request):
    contexto = {
        'title': 'Policia Militar'
    }
    return render(request, "militar.html", contexto)