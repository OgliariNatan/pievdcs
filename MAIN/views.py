from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
#from ..seguranca_publica.models.base import Vitima_dados
from seguranca_publica.models.base import Vitima_dados
from django.db import models, connection

import random

print(connection.vendor)
@login_required
def home(request):
    context = {
        "title": "Página Inicial",
        "welcome_message": "Bem-vindo à Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais!",
        'encaminhamentos': 0, #Criar variaveis para encaminhamentos
        'alert': 0, #criar variavel para notificações
    }
    return render(request, "home.html", context)

def index(request):
    context = {
        "title": "Bem-vindo",
        "description": "Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais"
    }
    return render(request, "index.html", context)

@login_required
def encaminhamentos(request):
    context = {
        "title": "Encaminhamentos",
        "description": "Visualize os encaminhamentos realizados na plataforma.",
        'user': request.user,
    }
    return render(request, "encaminhamentos.html", context)

@login_required
def notificacoes(request, notificacoes=0):
    context = {
        "title": "Notificações",
        "description": "Visualize as notificações recebidas na plataforma.",
        'notificacao': [notificacoes],
        'user': request.user,
    }
    return render(request, "notificacoes.html", context)

def relatorios(request):
    """
        Renderiza a página de relatórios com dados estatísticos.
    """
    quantidade_de_vitimas = Vitima_dados.objects.count()
    print(f'Banco em uso: {connection.vendor}')
    print(quantidade_de_vitimas)
    print(f'Nome das Vitimas: {Vitima_dados.objects.values_list("idade", 'nome')}')

    extrai_grupo_etnico = Vitima_dados.objects.values_list('etnia', flat=True)
    print(f'Grupo étnico: {extrai_grupo_etnico}')

    context = {
        "title": "Painel Informativo",
        "description": "Visualize o painel informativo estatístico gerados na plataforma.",

        "periodo": ['Todos', 'Semanal', 'Mensal', 'Anual'],

        "comarcas": ["Todas", "Abelardo Luz", "Anchieta", "Anita Garibaldi", "Araquari", "Araranguá", "Armazém", "Ascurra", "Balneário Camboriú", "Balneário Piçarras", "Barra Velha", "Biguaçu", "Blumenau - Foro Central", "Blumenau - Fórum Universitário", "Bom Retiro", "Braço do Norte", "Brusque", "Caçador", "Camboriú", "Campo Belo do Sul", "Campo Erê", "Campos Novos", "Canoinhas", "Capinzal", "Capital", "Capital - Estadual Bancário", "Capital - Continente", "Capital - Eduardo Luz", "Capital - Norte da Ilha", "Capivari de Baixo", "Catanduvas", "Chapecó", "Concórdia", "Coronel Freitas", "Correia Pinto", "Criciúma", "Cunha Porã", "Curitibanos", "Descanso", "Dionísio Cerqueira", "Forquilhinha", "Fraiburgo", "Garopaba", "Garuva", "Gaspar", "Guaramirim", "Herval D'Oeste", "Ibirama", "Içara", "Imaruí", "Imbituba", "Indaial", "Ipumirim", "Itá", "Itaiópolis", "Itajaí", "Itapema", "Itapiranga", "Itapoá", "Ituporanga", "Jaguaruna", "Jaraguá do Sul", "Joaçaba", "Joinville", "Joinville - Fórum Fazendário", "Lages", "Laguna", "Lauro Müller", "Lebon Régis", "Mafra", "Maravilha", "Meleiro", "Modelo", "Mondaí", "Navegantes", "Orleans", "Otacílio Costa", "Palhoça", "Palmitos", "Papanduva", "Penha", "Pinhalzinho", "Pomerode", "Ponte Serrada", "Porto Belo", "Porto União", "Presidente Getúlio", "Quilombo", "Rio do Campo", "Rio do Oeste", "Rio do Sul", "Rio Negrinho", "Santa Cecília", "Santa Rosa do Sul", "Santo Amaro da Imperatriz", "São Bento do Sul", "São Carlos", "São Domingos", "São Francisco do Sul", "São João Batista", "São Joaquim", "São José", "São José do Cedro", "São Lourenço do Oeste", "São Miguel do Oeste", "Seara", "Sombrio", "Taió", "Tangará", "Tijucas", "Timbó", "Trombudo Central", "Tubarão", "Turvo", "Urubici", "Urussanga", "Videira", "Xanxerê", "Xaxim"],

        "quantidade_de_vitimas": [quantidade_de_vitimas],
        "cidades": {
            "labels": ["Maravilha", "Tigrinhos", "Iraceminha", "Santa Terezinha do Progresso", "São Miguel da Boa Vista", "Flor do Sertão"],
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
            "labels": ["Abaixo de R$1.518,00", "De R$3.636,00 a R$1.518,00", "De R$3.636,01 a R$7.017,63", "De R$7.017,64 a R$28.239,99", "Acima de R$28.240,00"],
            "data": [random.randint(1,90), random.randint(1,110), random.randint(1,50), random.randint(1,5), random.randint(1,5)]
        },

        "bairros": [
            {"nome": "Bairro 1", "lat": -26.771567, "lng": -53.190010, "casos": 10},
            {"nome": "Bairro 2", "lat": -26.7670, "lng": -53.1850, "casos": 20},
            {"nome": "Bairro 3", "lat": -26.7690, "lng": -53.1810, "casos": 15},
            {"nome": "Bairro 4", "lat": -26.7630, "lng": -53.1870, "casos": 25},
            {"nome": "Linha Sanga Silva", "lat": -26.73157, "lng": -53.19992, "casos": 1},
            {"nome": "Iraceminha", "lat": -26.823437, "lng": -53.273439, "casos": 5},
            {"nome": "Flor do Sertão", "lat": -26.777475, "lng": -53.349358, "casos": 2},
            {"nome": "São Miguel da Boa Vista", "lat": -26.692041, "lng": -53.257654, "casos": 3},
            {"nome": "Tigrinhos", "lat": -26.686780, "lng": -53.157091, "casos": 8},
            {"nome": "Santa Terezinha do Progresso", "lat": -26.618440, "lng": -53.198218, "casos": 4},
        ],
        
        "Tipos_de_Violência": {
            "labels": ["Física", "Psicológica", "Sexual", "Patrimonial", "Moral"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,50)]
        },

        "parentesco_do_agressor": { #parentescoChart
            "labels": ["Pai", "Tio", "Cônjuge", "Filho", "Cunhado", "Padrastro", "Outros"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,10)]
        },
        "grauInstrucao": { #grauInstrucaoChart
            "labels": ["Não Alfabetizado", "Fundamental", "Médio", "Superior", "Pós-graduação"],
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
    