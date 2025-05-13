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
            "labels": ["0-13", "14-18", "19-30", "31-50", "51+"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100)]
        },
        
        "etnias": {
            "labels": ["Branca", "Parda", "Preta", "Amarela", "Indígena"],
            "data": [random.randint(1,10), random.randint(1,100), random.randint(1,100), random.randint(1,10), random.randint(1,50)]
        },

        "classeEconomica": { #classeEconomicaChart
            "labels": ["Acima de R$28.240,00", "De R$7.017,64 a R$28.239,99", "De R$3.636,01 a R$7.017,63", "De R$3.636,00 a R$1.518,00", "Abaixo de R$1.518,00"],
            "data": [random.randint(1,5), random.randint(1,10), random.randint(1,150), random.randint(1,150), random.randint(1,50)]
        },

        "bairros": [
            {"nome": "Bairro 1", "lat": -26.7650, "lng": -53.1830, "casos": 10},
            {"nome": "Bairro 2", "lat": -26.7670, "lng": -53.1850, "casos": 20},
            {"nome": "Bairro 3", "lat": -26.7690, "lng": -53.1810, "casos": 15},
            {"nome": "Bairro 4", "lat": -26.7630, "lng": -53.1870, "casos": 25},
        ],
        
        "Tipos_de_Violência": {
            "labels": ["Física", "Psicológica", "Sexual", "Econômica", "Patrimonial", "Moral"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,50)]
        },

        "parentesco_do_agressor": { #parentescoChart
            "labels": ["Pai", "Tio", "Cônjuge", "Filho", "Cunhado", "Padrastro", "Outros"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,10)]
        },
        "grauInstrucao": { #grauInstrucaoChart
            "labels": ["Analfabeto", "Fundamental", "Médio", "Superior", "Pós-graduação"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,10), random.randint(1,10)]
        },
    }
    return render(request, "relatorios.html", context)


#Destinado a recuperação de senha
class CustomPasswordResetView:

    template_nome = 'registration/password_reset_form.html'
    email_template_nome = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done.html')
    