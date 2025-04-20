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
        "description": "Visualize os relatórios gerados na plataforma.",
        "cidades": {
            "labels": ["Cidade A", "Cidade B", "Cidade C", "Cidade D"],
            "data": [30, 20, 25, 25]
        },
        "idades": {
            "labels": ["0-18", "19-30", "31-50", "51+"],
            "data": [15, 40, 30, 15]
        },
        "etnias": {
            "labels": ["Etnia A", "Etnia B", "Etnia C", "Etnia D"],
            "data": [10, 25, 35, 30]
        }
    }
    return render(request, "relatorios.html", context)