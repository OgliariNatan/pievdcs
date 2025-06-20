# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from collections import defaultdict
from sistema_justica.models.base import Vitima_dados
from seguranca_publica.models.militar import OcorrenciaMilitar
from seguranca_publica.models.civil import OcorrenciaCivil
from django.db import models, connection
from .models import ConteudoHome
import random



print(f'\n\nBanco em uso: {connection.vendor}\n\n--------------------------------------------')



def index(request):
    context = {
        "title": "Bem-vindo",
        "description": "Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais"
    }
    return render(request, "index.html", context)


def index_controlador(request):
    """
        Renderiza a página inicial com os conteúdos da página inicial.
    """
    #itens  = ConteudoHome.objects.filter(publicado=True).order_by('-data_publicacao')
    itens = ConteudoHome.objects.all().order_by('-data_publicacao')
    conteudos = defaultdict(list)

    for item in itens:
        conteudos[item.secao].append(item)

    context = {
        "conteudos": conteudos,
        "title": "Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais",
        "description": "Página Inicial",
    }
    return render(request, "index_controlador.html", context)



def pre_visualizacao_conteudo(request, pk):
    """
        Renderiza a pré-visualização de um conteúdo específico da página inicial.
    """
    try:
        conteudo = get_object_or_404(ConteudoHome, pk=pk)
    except ConteudoHome.DoesNotExist:
        return HttpResponse("Conteúdo não encontrado.", status=404)

    context = {
        "conteudo": conteudo,
        "title": "Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais",
        "description": "Pré-visualização do Conteúdo",
    }
    return render(request, "pre_visualizacao_conteudo.html", context)


@login_required
def home(request):
    context = {
        "title": "Página Inicial",
        "welcome_message": "Bem-vindo à Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais!",
        'encaminhamentos': 0, #Criar variaveis para encaminhamentos
        'alert': 0, #criar variavel para notificações
    }
    return render(request, "home.html", context)


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
    
    

    context = {
        "title": "Painel Informativo",
        "description": "Visualize o painel informativo estatístico gerados na plataforma.",

        "periodo": ['Todos', 'Semanal', 'Mensal', 'Anual'],

        "comarcas": ["Todas", "Abelardo Luz", "Anchieta", "Anita Garibaldi", "Araquari", "Araranguá", "Armazém", "Ascurra", "Balneário Camboriú", "Balneário Piçarras", "Barra Velha", "Biguaçu", "Blumenau - Foro Central", "Blumenau - Fórum Universitário", "Bom Retiro", "Braço do Norte", "Brusque", "Caçador", "Camboriú", "Campo Belo do Sul", "Campo Erê", "Campos Novos", "Canoinhas", "Capinzal", "Capital", "Capital - Estadual Bancário", "Capital - Continente", "Capital - Eduardo Luz", "Capital - Norte da Ilha", "Capivari de Baixo", "Catanduvas", "Chapecó", "Concórdia", "Coronel Freitas", "Correia Pinto", "Criciúma", "Cunha Porã", "Curitibanos", "Descanso", "Dionísio Cerqueira", "Forquilhinha", "Fraiburgo", "Garopaba", "Garuva", "Gaspar", "Guaramirim", "Herval D'Oeste", "Ibirama", "Içara", "Imaruí", "Imbituba", "Indaial", "Ipumirim", "Itá", "Itaiópolis", "Itajaí", "Itapema", "Itapiranga", "Itapoá", "Ituporanga", "Jaguaruna", "Jaraguá do Sul", "Joaçaba", "Joinville", "Joinville - Fórum Fazendário", "Lages", "Laguna", "Lauro Müller", "Lebon Régis", "Mafra", "Maravilha", "Meleiro", "Modelo", "Mondaí", "Navegantes", "Orleans", "Otacílio Costa", "Palhoça", "Palmitos", "Papanduva", "Penha", "Pinhalzinho", "Pomerode", "Ponte Serrada", "Porto Belo", "Porto União", "Presidente Getúlio", "Quilombo", "Rio do Campo", "Rio do Oeste", "Rio do Sul", "Rio Negrinho", "Santa Cecília", "Santa Rosa do Sul", "Santo Amaro da Imperatriz", "São Bento do Sul", "São Carlos", "São Domingos", "São Francisco do Sul", "São João Batista", "São Joaquim", "São José", "São José do Cedro", "São Lourenço do Oeste", "São Miguel do Oeste", "Seara", "Sombrio", "Taió", "Tangará", "Tijucas", "Timbó", "Trombudo Central", "Tubarão", "Turvo", "Urubici", "Urussanga", "Videira", "Xanxerê", "Xaxim"],

        "medidas_protetivas_solicitadas_ocorrencias": 
            OcorrenciaMilitar.objects.filter(status_MP='SO').count() + OcorrenciaCivil.objects.filter(status_MP='SO').count(),
        
        "cidades": {
            "labels": ["Maravilha", "Tigrinhos", "Iraceminha", "Santa Terezinha do Progresso", "São Miguel da Boa Vista", "Flor do Sertão"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100)]
        },

        "idades": {
            "labels": ["0-13", "14-18", "19-30", "31-50", "51+"],
            "data": [
                OcorrenciaMilitar.objects.filter(vitima__idade__range=(0, 13)).count() + OcorrenciaCivil.objects.filter(vitima__idade__range=(0, 13)).count(),
                OcorrenciaMilitar.objects.filter(vitima__idade__range=(14, 18)).count() + OcorrenciaCivil.objects.filter(vitima__idade__range=(14, 18)).count(),
                OcorrenciaMilitar.objects.filter(vitima__idade__range=(19, 30)).count() + OcorrenciaCivil.objects.filter(vitima__idade__range=(19, 30)).count(),
                OcorrenciaMilitar.objects.filter(vitima__idade__range=(31, 50)).count() + OcorrenciaCivil.objects.filter(vitima__idade__range=(31, 50)).count(),
                OcorrenciaMilitar.objects.filter(vitima__idade__gte=51).count() + OcorrenciaCivil.objects.filter(vitima__idade__gte=51).count(),
            ]
            #"data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100)]
        },
        
        "etnias": {
            "labels": ["Branca", "Parda", "Preta", "Amarela", "Indígena"],
            #"data": [random.randint(1,10), random.randint(1,100), random.randint(1,100), random.randint(1,10), random.randint(1,10)]
            "data": [
                OcorrenciaMilitar.objects.filter(vitima__etnia='BR').count() + OcorrenciaCivil.objects.filter(vitima__etnia='BR').count(),
                OcorrenciaMilitar.objects.filter(vitima__etnia='PA').count() + OcorrenciaCivil.objects.filter(vitima__etnia='PA').count(),
                OcorrenciaMilitar.objects.filter(vitima__etnia='PR').count() + OcorrenciaCivil.objects.filter(vitima__etnia='PR').count(),
                OcorrenciaMilitar.objects.filter(vitima__etnia='AM').count() + OcorrenciaCivil.objects.filter(vitima__etnia='AM').count(),
                OcorrenciaMilitar.objects.filter(vitima__etnia='IN').count() + OcorrenciaCivil.objects.filter(vitima__etnia='IN').count(),
            ]
        },

        "classeEconomica": { #classeEconomicaChart
            "labels": ["Sem Renda", "Abaixo de R$1.518,00", "De R$3.636,00 a R$1.518,00", "De R$3.636,01 a R$7.017,63", "De R$7.017,64 a R$28.239,99", "Acima de R$28.240,00"],
            #"data": [random.randint(1,90), random.randint(1,110), random.randint(1,50), random.randint(1,5), random.randint(1,5)]
            "data": [
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='SR').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='SR').count(),
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='AB').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='AB').count(),
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='BA').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='BA').count(),
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='BC').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='BC').count(),
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='BD').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='BD').count(),
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='AC').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='AC').count(),
            ]
        },

        "bairros": [ #Implementar na localidade da ocorrencia e local neutro, não no local exato da ocorrencia
            {"nome": "Novo Bairro", "lat": -26.771567, "lng": -53.190010, "casos": 10},
            {"nome": "Centro", "lat": -26.7670, "lng": -53.1850, "casos": 20},
            {"nome": "Morada do Sol", "lat": -26.7690, "lng": -53.1700, "casos": 15},
            {"nome": "Padre Antonio", "lat": -26.7630, "lng": -53.1870, "casos": 25},
            {"nome": "Linha Sanga Silva", "lat": -26.73157, "lng": -53.19992, "casos": 1},
            {"nome": "Iraceminha", "lat": -26.823437, "lng": -53.273439, "casos": 5},
            {"nome": "Flor do Sertão", "lat": -26.777475, "lng": -53.349358, "casos": 2},
            {"nome": "São Miguel da Boa Vista", "lat": -26.692041, "lng": -53.257654, "casos": 3},
            {"nome": "Tigrinhos", "lat": -26.686780, "lng": -53.157091, "casos": 8},
            {"nome": "Santa Terezinha do Progresso", "lat": -26.618440, "lng": -53.198218, "casos": 4},
        ],
        
        "Tipos_de_Violência": {
            "labels": ["Física", "Psicológica", "Sexual", "Patrimonial", "Moral"],
            "data": [
                OcorrenciaMilitar.objects.filter(tipo_de_violencia='Fisica').count() + OcorrenciaCivil.objects.filter(tipo_de_violencia='Fisica').count(),
                OcorrenciaMilitar.objects.filter(tipo_de_violencia='Psicologica').count() + OcorrenciaCivil.objects.filter(tipo_de_violencia='Psicologica').count(),
                OcorrenciaMilitar.objects.filter(tipo_de_violencia='Sexual').count() + OcorrenciaCivil.objects.filter(tipo_de_violencia='Sexual').count(),
                OcorrenciaMilitar.objects.filter(tipo_de_violencia='Patrimonial').count() + OcorrenciaCivil.objects.filter(tipo_de_violencia='Patrimonial').count(),
                OcorrenciaMilitar.objects.filter(tipo_de_violencia='Moral').count()  + OcorrenciaCivil.objects.filter(tipo_de_violencia='Moral').count(),
            ]
            #"data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,50)]
        },

        "parentesco_do_agressor": { #parentescoChart
            "labels": ["Pai", "Tio", "Cônjuge", "Filho", "Cunhado", "Padrastro", "Outros"],
            "data": [  
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Pai').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Pai').count(), 
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Tio').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Tio').count(), 
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Conjuge').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Conjuge').count(), 
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Filho').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Filho').count(),
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Cunhado').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Cunhado').count(),
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Padasto').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Padasto').count(), 
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Outros').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Outros').count(),
            ]
            #"data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,10)]
        },
        "grauInstrucao": { #grauInstrucaoChart
            "labels": ["Não Alfabetizado", "Fundamental Incompleto", "Fundamental Completo", "Médio Incompleto", "Médio Completo", "Superior Incompleto", "Superior Completo", "Pós-graduação"],
            #"data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,10), random.randint(1,10)]
            "data": [
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='AN').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='FI').count(), 
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='FI').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='FI').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='FC').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='FC').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='EI').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='EI').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='EC').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='EC').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='SU').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='SU').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='SS').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='SS').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='PO').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='PO').count(),
            ]
        },
    }
    return render(request, "relatorios.html", context)


#Destinado a recuperação de senha
class CustomPasswordResetView:

    template_nome = 'registration/password_reset_form.html'
    email_template_nome = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done.html')
    