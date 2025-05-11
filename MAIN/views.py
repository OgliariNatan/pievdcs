from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

import random

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
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100)]
        },

        "idades": {
            "labels": ["0-18", "19-30", "31-50", "51+", "51+"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100)]
        },
        
        "etnias": {
            "labels": ["Branca", "Parda", "Preta", "Amarela", "Indígena"],
            "data": [random.randint(1,10), random.randint(1,100), random.randint(1,100), random.randint(1,10), random.randint(1,50)]
        },

        "bairros": [
            {"nome": "Bairro 1", "lat": -26.7650, "lng": -53.1830, "casos": 10},
            {"nome": "Bairro 2", "lat": -26.7670, "lng": -53.1850, "casos": 20},
            {"nome": "Bairro 3", "lat": -26.7690, "lng": -53.1810, "casos": 15},
            {"nome": "Bairro 4", "lat": -26.7630, "lng": -53.1870, "casos": 25},
        ],
        
        "Tipos_de_Violência": {
            "labels": ["Física", "Psicológica", "Sexual", "Econômica"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100)]
        },

        "parentesco_do_agressor": { #parentescoChart
            "labels": ["Pai", "Tio", "Cônjuge", "Filho", "Cunhado", "Padrastro"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100)]
        },
    }
    return render(request, "relatorios.html", context)


#Destinado a recuperação de senha
class CustomPasswordResetView:

    template_nome = 'registration/password_reset_form.html'
    email_template_nome = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done.html')
    