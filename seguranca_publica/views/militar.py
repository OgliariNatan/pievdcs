from django.shortcuts import render

def militar(request):
    contexto = {
        'title': 'Polícia Militar'
    }
    return render(request, "militar.html", contexto)