from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    context = {
        "title": "Página Inicial",
        "welcome_message": "Bem-vindo à Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais!",
        'encaminhamentos': 3, #Criar variaveis para encaminhamentos
        'alert': 4, #criar variavel para notificações
    }
    return render(request, "home.html", context)

def index(request):
    context = {
        "title": "Bem-vindo",
        "description": "Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais"
    }
    return render(request, "index.html", context)


def relatorios(request):
    context = {
        "title": "Relatórios",
        "description": "Visualize os relatórios gerados na plataforma."
    }
    return render(request, "relatorios.html", context)