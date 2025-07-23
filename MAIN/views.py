# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from collections import defaultdict
from sistema_justica.models.base import Vitima_dados
from seguranca_publica.models.militar import OcorrenciaMilitar
from seguranca_publica.models.civil import OcorrenciaCivil
from seguranca_publica.models.penal import ModeloPenal
from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from django.db import models, connection
from .models import ConteudoHome
from .calculo_variaveis import *
import random



print(f'\n\nBanco em uso: {connection.vendor}\n\n--------------------------------------------')

def index_tailwind(request):
    """
        Renderiza a página inicial com os conteúdos da página inicial.
    """
    itens  = ConteudoHome.objects.filter(publicado=True).order_by('secao','-data_publicacao')
    
    conteudos = defaultdict(list)
    
    for item in itens:
        conteudos[item.secao].append(item)

    conteudos = dict(conteudos) 

    medidas_protetivas_solicitadas_ocorrencias = (
        OcorrenciaMilitar.objects.filter(status_MP='SO').count() + 
        OcorrenciaCivil.objects.filter(status_MP='SO').count() + 
        FormularioMedidaProtetiva.objects.filter(solicitada_mpu=True).count()
    )

    grupos_atendidos = ModeloPenal.objects.all().count()


    context = {
        "conteudos": conteudos,
        "title": "Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais",
        "description": "Página Inicial",
        'medidas_protetivas_solicitadas_ocorrencias': medidas_protetivas_solicitadas_ocorrencias,
        'encaminhamentos': random.randint(1,100),  # Criar variaveis para encaminhamentos
        'casos_mediados': random.randint(1,100),  # Criar variavel para casos mediados
        'atendimentos': grupos_atendidos
    }
    return render(request, "index_tailwind.html", context)



def index(request):
    """
    Subistituido pelo index_controlador
    """
    context = {
        "title": "Bem-vindo",
        "description": "Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais"
    }
    return render(request, "index.html", context)


def index_controlador(request):
    """
        Renderiza a página inicial com os conteúdos da página inicial.
    """
    itens  = ConteudoHome.objects.filter(publicado=True).order_by('secao','-data_publicacao')
    #itens = ConteudoHome.objects.all().order_by('-data_publicacao')
    conteudos = defaultdict(list)

    for item in itens:
        conteudos[item.secao].append(item)

    conteudos = dict(conteudos) 
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
    
    dois_municipio = municipiosviolentos.municipios_mais_violentos(2)
    municipio_primeiro=dois_municipio[0][0]
    municipio_segundo=dois_municipio[1][0]


    resultado_verifica = tipoviolencia.verifica_maior_violencia_por_mes()
    tipo_violencia_1 = resultado_verifica['mes_atual']['tipo']
    tipo_violencia_1_total = resultado_verifica['mes_atual']['total']
    tipo_violencia_1_porcentagem = resultado_verifica['mes_anterior']['porcentagem']

    medidas_protetivas_calculo = medidasprotetivas.porcentagem_mes_anterior()
    medidas_protetivas_solicitadas_ocorrencias = medidas_protetivas_calculo['total']
    medidas_protetivas_solicitadas_ocorrencias_porcentagem = medidas_protetivas_calculo['porcentagem']

    grau_parentesco_comum = grauparentesco.parentesco_mais_comum()['grau_parentesco']

    context = {
        "title": "Painel Informativo",
        "description": "Visualize o painel informativo estatístico gerados na plataforma.",

        "periodo": ['Todos', 'Semanal', 'Mensal', 'Anual'],

        "comarcas": ComarcasPoderJudiciario.objects.values_list('nome', flat=True).order_by('nome'),  
        
        "medidas_protetivas_solicitadas_ocorrencias_porcentagem": medidas_protetivas_solicitadas_ocorrencias_porcentagem,
        "medidas_protetivas_solicitadas_ocorrencias": medidas_protetivas_solicitadas_ocorrencias,
        "municipio_primeiro": municipio_primeiro,
        "municipio_segundo": municipio_segundo,
        "grau_parentesco_comum": grau_parentesco_comum,

        
        "cidades": {
            "labels": ["Maravilha", "Tigrinhos", "Iraceminha", "Santa Terezinha do Progresso", "São Miguel da Boa Vista", "Flor do Sertão"],
            "data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100)]
        },

        "idades": {
            "labels": ["0-13", "14-18", "19-30", "31-50", "51+"],
            "data": [
                OcorrenciaMilitar.objects.filter(vitima__idade__range=(0, 13)).count() + OcorrenciaCivil.objects.filter(vitima__idade__range=(0, 13)).count() + FormularioMedidaProtetiva.objects.filter(vitima__idade__range=(0, 13)).count(),

                OcorrenciaMilitar.objects.filter(vitima__idade__range=(14, 18)).count() + OcorrenciaCivil.objects.filter(vitima__idade__range=(14, 18)).count() + FormularioMedidaProtetiva.objects.filter(vitima__idade__range=(14, 18)).count(),

                OcorrenciaMilitar.objects.filter(vitima__idade__range=(19, 30)).count() + OcorrenciaCivil.objects.filter(vitima__idade__range=(19, 30)).count() + FormularioMedidaProtetiva.objects.filter(vitima__idade__range=(19, 30)).count(),

                OcorrenciaMilitar.objects.filter(vitima__idade__range=(31, 50)).count() + OcorrenciaCivil.objects.filter(vitima__idade__range=(31, 50)).count() + FormularioMedidaProtetiva.objects.filter(vitima__idade__range=(31, 50)).count(),

                OcorrenciaMilitar.objects.filter(vitima__idade__gte=51).count() + OcorrenciaCivil.objects.filter(vitima__idade__gte=51).count() + FormularioMedidaProtetiva.objects.filter(vitima__idade__gte=51).count(),
            ]
            #"data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100)]
        },
        
        "etnias": {
            "labels": ["Branca", "Parda", "Preta", "Amarela", "Indígena"],
            "data": [
                OcorrenciaMilitar.objects.filter(vitima__etnia='BR').count() + OcorrenciaCivil.objects.filter(vitima__etnia='BR').count() + FormularioMedidaProtetiva.objects.filter(vitima__etnia='BR').count(),
                OcorrenciaMilitar.objects.filter(vitima__etnia='PA').count() + OcorrenciaCivil.objects.filter(vitima__etnia='PA').count() + FormularioMedidaProtetiva.objects.filter(vitima__etnia='PA').count(),
                OcorrenciaMilitar.objects.filter(vitima__etnia='PR').count() + OcorrenciaCivil.objects.filter(vitima__etnia='PR').count() + FormularioMedidaProtetiva.objects.filter(vitima__etnia='PR').count(),
                OcorrenciaMilitar.objects.filter(vitima__etnia='AM').count() + OcorrenciaCivil.objects.filter(vitima__etnia='AM').count() + FormularioMedidaProtetiva.objects.filter(vitima__etnia='AM').count(),
                OcorrenciaMilitar.objects.filter(vitima__etnia='IN').count() + OcorrenciaCivil.objects.filter(vitima__etnia='IN').count() + FormularioMedidaProtetiva.objects.filter(vitima__etnia='IN').count(),
            ]
        },

        "classeEconomica": { #classeEconomicaChart
            "labels": ["Sem Renda", "Abaixo de R$1.518,00", "De R$3.636,00 a R$1.518,00", "De R$3.636,01 a R$7.017,63", "De R$7.017,64 a R$28.239,99", "Acima de R$28.240,00"],
            "data": [
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='SR').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='SR').count() + FormularioMedidaProtetiva.objects.filter(vitima__classeEconomica='SR').count(),
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='AB').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='AB').count() + FormularioMedidaProtetiva.objects.filter(vitima__classeEconomica='AB').count(),
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='BA').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='BA').count() + FormularioMedidaProtetiva.objects.filter(vitima__classeEconomica='BA').count(),
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='BC').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='BC').count() + FormularioMedidaProtetiva.objects.filter(vitima__classeEconomica='BC').count(),
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='BD').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='BD').count() + FormularioMedidaProtetiva.objects.filter(vitima__classeEconomica='BD').count(),
                OcorrenciaMilitar.objects.filter(vitima__classeEconomica='AC').count() + OcorrenciaCivil.objects.filter(vitima__classeEconomica='AC').count() + FormularioMedidaProtetiva.objects.filter(vitima__classeEconomica='AC').count(),
            ]
        },

        "bairros": [ #Implementar na localidade da ocorrencia e local neutro, não no local exato da ocorrencia
            {"nome": "Novo Bairro", "lat": -26.771567, "lng": -53.190010, "casos": 10, "tipo_violencia": "Física"},
            {"nome": "Centro", "lat": -26.7670, "lng": -53.1850, "casos": 20, "tipo_violencia": "Psicológica"},
            {"nome": "Morada do Sol", "lat": -26.7690, "lng": -53.1700, "casos": 15, "tipo_violencia": "Sexual"},
            {"nome": "Padre Antonio", "lat": -26.7630, "lng": -53.1870, "casos": 25, "tipo_violencia": "Patrimonial"},
            {"nome": "Linha Sanga Silva", "lat": -26.73157, "lng": -53.19992, "casos": 1, "tipo_violencia": "Moral"},
            {"nome": "Iraceminha", "lat": -26.823437, "lng": -53.273439, "casos": 5, "tipo_violencia": "Física"},
            {"nome": "Flor do Sertão", "lat": -26.777475, "lng": -53.349358, "casos": 2, "tipo_violencia": "Patrimonial"}      ,
            {"nome": "São Miguel da Boa Vista", "lat": -26.692041, "lng": -53.257654, "casos": 3, "tipo_violencia": "Moral"},
            {"nome": "Tigrinhos", "lat": -26.686780, "lng": -53.157091, "casos": 8, "tipo_violencia": "Física"},
            {"nome": "Santa Terezinha do Progresso", "lat": -26.618440, "lng": -53.198218, "casos": 4, "tipo_violencia": "Psicológica"},
        ],
        
        "Tipos_de_Violência": {
            "labels": ["Física", "Psicológica", "Sexual", "Patrimonial", "Moral"],
            "data": [
                OcorrenciaMilitar.objects.filter(tipo_de_violencia='Fisica').count() + OcorrenciaCivil.objects.filter(tipo_de_violencia='Fisica').count() + FormularioMedidaProtetiva.objects.filter(tipo_de_violencia='Fisica').count(),
                OcorrenciaMilitar.objects.filter(tipo_de_violencia='Psicologica').count() + OcorrenciaCivil.objects.filter(tipo_de_violencia='Psicologica').count() + FormularioMedidaProtetiva.objects.filter(tipo_de_violencia='Psicologica').count(),
                OcorrenciaMilitar.objects.filter(tipo_de_violencia='Sexual').count() + OcorrenciaCivil.objects.filter(tipo_de_violencia='Sexual').count() + FormularioMedidaProtetiva.objects.filter(tipo_de_violencia='Sexual').count(),
                OcorrenciaMilitar.objects.filter(tipo_de_violencia='Patrimonial').count() + OcorrenciaCivil.objects.filter(tipo_de_violencia='Patrimonial').count() + FormularioMedidaProtetiva.objects.filter(tipo_de_violencia='Patrimonial').count(),
                OcorrenciaMilitar.objects.filter(tipo_de_violencia='Moral').count()  + OcorrenciaCivil.objects.filter(tipo_de_violencia='Moral').count() + FormularioMedidaProtetiva.objects.filter(tipo_de_violencia='Moral').count(),
            ]
            #"data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,50)]
        },
        "tipo_violencia_1" : tipo_violencia_1,
        "tipo_violencia_1_total" : tipo_violencia_1_total,
        "tipo_violencia_1_porcentagem" : tipo_violencia_1_porcentagem,

        "parentesco_do_agressor": { #parentescoChart
            "labels": ["Pai", "Tio", "Cônjuge", "Filho", "Cunhado", "Padrastro", "Outros"],
            "data": [  
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Pai').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Pai').count() + FormularioMedidaProtetiva.objects.filter(grau_parentesco_agressor='Pai').count(), 
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Tio').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Tio').count() + FormularioMedidaProtetiva.objects.filter(grau_parentesco_agressor='Tio').count(), 
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Conjuge').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Conjuge').count() + FormularioMedidaProtetiva.objects.filter(grau_parentesco_agressor='Conjuge').count(), 
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Filho').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Filho').count() + FormularioMedidaProtetiva.objects.filter(grau_parentesco_agressor='Filho').count(),
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Cunhado').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Cunhado').count() + FormularioMedidaProtetiva.objects.filter(grau_parentesco_agressor='Cunhado').count(),
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Padasto').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Padasto').count() + FormularioMedidaProtetiva.objects.filter(grau_parentesco_agressor='Padasto').count(),
                OcorrenciaMilitar.objects.filter(grau_parentesco_agressor='Outros').count() + OcorrenciaCivil.objects.filter(grau_parentesco_agressor='Outros').count() + FormularioMedidaProtetiva.objects.filter(grau_parentesco_agressor='Outros').count(),
            ]
            #"data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,10)]
        },
        "grauInstrucao": { #grauInstrucaoChart
            "labels": ["Não Alfabetizado", "Fundamental Incompleto", "Fundamental Completo", "Médio Incompleto", "Médio Completo", "Superior Incompleto", "Superior Completo", "Pós-graduação"],
            #"data": [random.randint(1,100), random.randint(1,100), random.randint(1,100), random.randint(1,10), random.randint(1,10)]
            "data": [
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='AN').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='AN').count() + FormularioMedidaProtetiva.objects.filter(vitima__escolaridade='AN').count(), 
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='FI').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='FI').count() + FormularioMedidaProtetiva.objects.filter(vitima__escolaridade='FI').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='FC').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='FC').count() + FormularioMedidaProtetiva.objects.filter(vitima__escolaridade='FC').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='EI').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='EI').count() + FormularioMedidaProtetiva.objects.filter(vitima__escolaridade='EI').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='EC').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='EC').count() + FormularioMedidaProtetiva.objects.filter(vitima__escolaridade='EC').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='SU').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='SU').count() + FormularioMedidaProtetiva.objects.filter(vitima__escolaridade='SU').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='SS').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='SS').count() + FormularioMedidaProtetiva.objects.filter(vitima__escolaridade='SS').count(),
                OcorrenciaMilitar.objects.filter(vitima__escolaridade='PO').count() + OcorrenciaCivil.objects.filter(vitima__escolaridade='PO').count() + FormularioMedidaProtetiva.objects.filter(vitima__escolaridade='PO').count(),
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

class CustomLoginView(LoginView):
    template_name = 'login.html'
    next_page = '/home/'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/home/')
        return super().dispatch(request, *args, **kwargs)