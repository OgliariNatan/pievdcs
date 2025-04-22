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
        "title": "Painel Informativo",
        "description": "Visualize o painel informativo estatístico gerados na plataforma.",
        "cidade_maps": "Maravilha/SC",
        "cidades": {
            "labels": ["Maravilha", "Tigrinhos", "Irceminha", "Santa Terezinha do Progresso", "São Miguel da Boa Vista", "Flor do Sertão"],
            "data": [60, 20, 30, 25, 15, 40]
        },
        "idades": {
            "labels": ["0-18", "19-30", "31-50", "51+", "51+"],
            "data": [15, 40, 30, 15, 10]
        },
        "etnias": {
            "labels": ["Etnia A", "Etnia B", "Etnia C", "Etnia D"],
            "data": [10, 25, 35, 30]
        },
        "bairros": [
            {"nome": "Bairro 1", "lat": -26.7650, "lng": -53.1830, "casos": 10},
            {"nome": "Bairro 2", "lat": -26.7670, "lng": -53.1850, "casos": 20},
            {"nome": "Bairro 3", "lat": -26.7690, "lng": -53.1810, "casos": 15},
            {"nome": "Bairro 4", "lat": -26.7630, "lng": -53.1870, "casos": 25},
        ]
    }
    return render(request, "relatorios.html", context)