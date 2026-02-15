# -*- coding: utf-8 -*-
"""  
    Modelo pertinente as visualizações  publicas
    dir: MAIN/views.py
    @author: OgliariNatan
"""
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from collections import defaultdict
from datetime import datetime, timedelta
from django.utils import timezone
from sistema_justica.models.base import Vitima_dados, TipoDeViolencia
from seguranca_publica.models.militar import OcorrenciaMilitar
from seguranca_publica.models.civil import OcorrenciaCivil
from seguranca_publica.models.penal import ModeloPenal
from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from django.db import connection
from django.db.models import Prefetch, Count, Q
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear
from .models import ConteudoHome
from usuarios.models import CustomUser
from .calculo_variaveis import *
import random
import time


""" Configuraçao de decoradores para debug """
import os

var_debug = os.getenv('DEBUG')
# \033[0m - reset
# \033[92m - verde
# \033[34m - azul
# \033[31m - vermelho
# \033[33m - amarelo
if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    print(30*'-')
    print(f'\nBanco em uso: {connection.vendor}\n')
    print(30*'-')
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
    #raise Exception("Debug ativado - interrompendo a execução para evitar lentidão.")
    
else:
    checked_debug_decorador = None
    checked_debug_decorador_fun = None

""" Fim da configuraçao de decoradores para debug """

@checked_debug_decorador
def index_tailwind(request):
    """
        Renderiza a página inicial com os conteúdos da página inicial.
    """
    
    try:
        itens  = ConteudoHome.objects.filter(publicado=True).order_by('secao','-data_publicacao')
    except Exception as e:
        if var_debug == 'True':
            print(f'Tipo de erro:{type(e).__name__}')
            print(f"Erro ao buscar conteúdos da página inicial: {e}")
        itens = []
    
    conteudos = defaultdict(list)

    for item in itens:
        conteudos[item.secao].append(item)

    conteudos = dict(conteudos) 

    try:
        medidas_protetivas_solicitadas_ocorrencias = (
            OcorrenciaMilitar.objects.filter(status_MP='SO').count() + 
            OcorrenciaCivil.objects.filter(status_MP='SO').count() + 
            FormularioMedidaProtetiva.objects.filter(solicitada_mpu=True).count()
        )
    except Exception as e:
        if var_debug == 'True':
            print(f'Tipo de erro:{type(e).__name__}')
            print(f"Erro ao calcular medidas protetivas: {e}")
        medidas_protetivas_solicitadas_ocorrencias = 0

    
    try:
        grupos_atendidos = ModeloPenal.objects.all().count()
    except Exception as e:
        if var_debug == 'True':
            print(f'Tipo de erro:{type(e).__name__}')
            print(f"Erro ao contar grupos atendidos: {e}")
        grupos_atendidos = 0


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

@checked_debug_decorador
@login_required
def home(request):
    usuario_conectado = request.user.is_authenticated
    if usuario_conectado == False:
        raise PermissionError("Usuário não autenticado tentando acessar a página home.")

    usuario_ativo = request.user.is_active
    if usuario_ativo == False:
        if var_debug == 'True':
            print(f"Usuário: {request.user}.") 
            print(f"IP: {request.META.get('REMOTE_ADDR')}")
        raise PermissionError("Usuário inativo tentando acessar a página home.")
          
        
    context = {
        "title": "Página Inicial pós Login",
        "welcome_message": "Bem-vindo à Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais!",
        
    }
    return render(request, "home.html", context)


@login_required
def encaminhamentos(request):
    
    usuario_conectado = request.user.is_authenticated
    if usuario_conectado == False:
        raise PermissionError("Usuário não autenticado tentando acessar a página de encaminhamentos.")

    usuario_ativo = request.user.is_active
    if usuario_ativo == False:
        if var_debug == 'True':
            print(f"Usuário: {request.user}.") 
            print(f"IP: {request.META.get('REMOTE_ADDR')}")
        raise PermissionError("Usuário inativo tentando acessar a página de encaminhamentos.")

    context = {
        "title": "Encaminhamentos",
        "description": "Visualize os encaminhamentos realizados na plataforma.",
        'user': request.user,
    }
    return render(request, "encaminhamentos.html", context)

@login_required
def notificacoes(request, notificacoes=0):
    usuario_conectado = request.user.is_authenticated
    if usuario_conectado == False:
        raise PermissionError("Usuário não autenticado tentando acessar a página de notificações.")

    usuario_ativo = request.user.is_active
    if usuario_ativo == False:
        if var_debug == 'True':
            print(f"Usuário: {request.user}.") 
            print(f"IP: {request.META.get('REMOTE_ADDR')}")
        raise PermissionError("Usuário inativo tentando acessar a página de notificações.")

    context = {
        "title": "Notificações",
        "description": "Visualize as notificações recebidas na plataforma.",
        'notificacao': [notificacoes],
        'user': request.user,
    }
    return render(request, "notificacoes.html", context)


def calcular_tendencia_temporal():
    """
    Calcula dados de tendência temporal dos últimos 24 meses.
    Retorna labels (meses) e dados (quantidade de casos).
    """
    hoje = timezone.now()
    
    # Gerar últimos 24 meses
    meses = []
    for i in range(23, -1, -1):
        data = hoje - timedelta(days=i*30)
        meses.append(data.replace(day=1))
    
    labels = []
    dados = []
    
    meses_pt = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    for mes in meses:
        inicio = mes
        if mes.month == 12:
            fim = mes.replace(year=mes.year + 1, month=1)
        else:
            fim = mes.replace(month=mes.month + 1)
        
        # Contagem por modelo
        count_pm = OcorrenciaMilitar.objects.filter(
            data__gte=inicio, data__lt=fim
        ).count()
        
        count_pc = OcorrenciaCivil.objects.filter(
            data__gte=inicio, data__lt=fim
        ).count()
        
        count_mp = FormularioMedidaProtetiva.objects.filter(
            data_solicitacao__gte=inicio, data_solicitacao__lt=fim
        ).count()
        
        total = count_pm + count_pc + count_mp
        
        label = f"{meses_pt[mes.month]}/{mes.year}"
        labels.append(label)
        dados.append(total)
    
    return {"labels": labels, "data": dados}


def aplicar_filtros_queryset(request):
    """
    Aplica filtros de período e comarca nos querysets.
    Retorna os querysets filtrados.
    """
    periodo = request.GET.get('periodo', 'Todos')
    comarca = request.GET.get('comarca', '')
    
    hoje = timezone.now()
    
    # Querysets base
    qs_pm = OcorrenciaMilitar.objects.all()
    qs_pc = OcorrenciaCivil.objects.all()
    qs_mp = FormularioMedidaProtetiva.objects.all()
    
    # Filtro de período
    if periodo == 'Semanal':
        data_inicio = hoje - timedelta(days=7)
        qs_pm = qs_pm.filter(data__gte=data_inicio)
        qs_pc = qs_pc.filter(data__gte=data_inicio)
        qs_mp = qs_mp.filter(data_solicitacao__gte=data_inicio)
        if var_debug == 'True':
            print(f"Aplicando filtro semanal: data_inicio={data_inicio}, hoje={hoje}")
            print(f'Conta MP: {qs_mp.count()}')
    elif periodo == 'Mensal':
        qs_pm = qs_pm.filter(data__month=hoje.month, data__year=hoje.year)
        qs_pc = qs_pc.filter(data__month=hoje.month, data__year=hoje.year)
        qs_mp = qs_mp.filter(data_solicitacao__month=hoje.month, data_solicitacao__year=hoje.year)
    elif periodo == 'Anual':
        qs_pm = qs_pm.filter(data__year=hoje.year)
        qs_pc = qs_pc.filter(data__year=hoje.year)
        qs_mp = qs_mp.filter(data_solicitacao__year=hoje.year)
        if var_debug == 'True':
            print(f"Aplicando filtro Anual: data_inicio={data_inicio}, hoje={hoje}")
            print(f'Conta MP: {qs_mp.count()}')
    if var_debug == 'True':
        print(f"Filtro aplicado: {periodo}. Contagem PM: {qs_pm.count()}, PC: {qs_pc.count()}, MP: {qs_mp.count()}")
    
    # Filtro de comarca (apenas MP tem comarca)
    if comarca and comarca != 'Todas':
        qs_mp = qs_mp.filter(comarca_competente__nome=comarca)
        qs_pc = qs_pc.filter(Q(comarca_competente__nome=comarca) | Q(comarca_competente__isnull=True))
    
    return qs_pm, qs_pc, qs_mp, periodo, comarca


def calcular_dados_graficos(qs_pm, qs_pc, qs_mp):
    """
    Calcula todos os dados para os gráficos baseado nos querysets filtrados.
    """
    # Tipos de Violência
    try:
        tipos_violencia_ativos = TipoDeViolencia.objects.filter(ativo=True).order_by('nome')
        label_violencia = [tipo.nome for tipo in tipos_violencia_ativos]
        ids_tipos = [tipo.id for tipo in tipos_violencia_ativos]
        
        pm_counts = dict(
            OcorrenciaMilitar.objects
            .filter(tipo_de_violencia__id__in=ids_tipos)
            .values('tipo_de_violencia__id')
            .annotate(total=Count('id'))
            .values_list('tipo_de_violencia__id', 'total')
        )
        
        pc_counts = dict(
            OcorrenciaCivil.objects
            .filter(tipo_de_violencia__id__in=ids_tipos)
            .values('tipo_de_violencia__id')
            .annotate(total=Count('id'))
            .values_list('tipo_de_violencia__id', 'total')
        )
        
        mp_counts = dict(
            FormularioMedidaProtetiva.objects
            .filter(tipo_de_violencia__id__in=ids_tipos)
            .values('tipo_de_violencia__id')
            .annotate(total=Count('ID'))
            .values_list('tipo_de_violencia__id', 'total')
        )
        
        dados_violencia = [
            pm_counts.get(tipo.id, 0) + pc_counts.get(tipo.id, 0) + mp_counts.get(tipo.id, 0)
            for tipo in tipos_violencia_ativos
        ]
    except Exception as e:
        if var_debug == 'True':
            print(f'Erro violência: {e}')
        label_violencia = []
        dados_violencia = []
    
    # Idades
    idades_data = {
        "labels": ["0-13", "14-18", "19-30", "31-50", "51+"],
        "data": [
            qs_pm.filter(vitima__idade__range=(0, 13)).count() + 
            qs_pc.filter(vitima__idade__range=(0, 13)).count() + 
            qs_mp.filter(vitima__idade__range=(0, 13)).count(),
            
            qs_pm.filter(vitima__idade__range=(14, 18)).count() + 
            qs_pc.filter(vitima__idade__range=(14, 18)).count() + 
            qs_mp.filter(vitima__idade__range=(14, 18)).count(),
            
            qs_pm.filter(vitima__idade__range=(19, 30)).count() + 
            qs_pc.filter(vitima__idade__range=(19, 30)).count() + 
            qs_mp.filter(vitima__idade__range=(19, 30)).count(),
            
            qs_pm.filter(vitima__idade__range=(31, 50)).count() + 
            qs_pc.filter(vitima__idade__range=(31, 50)).count() + 
            qs_mp.filter(vitima__idade__range=(31, 50)).count(),
            
            qs_pm.filter(vitima__idade__gte=51).count() + 
            qs_pc.filter(vitima__idade__gte=51).count() + 
            qs_mp.filter(vitima__idade__gte=51).count(),
        ]
    }
    
    # Etnias
    etnias_data = {
        "labels": ["Branca", "Parda", "Preta", "Amarela", "Indígena"],
        "data": [
            qs_pm.filter(vitima__etnia='BR').count() + qs_pc.filter(vitima__etnia='BR').count() + qs_mp.filter(vitima__etnia='BR').count(),
            qs_pm.filter(vitima__etnia='PA').count() + qs_pc.filter(vitima__etnia='PA').count() + qs_mp.filter(vitima__etnia='PA').count(),
            qs_pm.filter(vitima__etnia='PR').count() + qs_pc.filter(vitima__etnia='PR').count() + qs_mp.filter(vitima__etnia='PR').count(),
            qs_pm.filter(vitima__etnia='AM').count() + qs_pc.filter(vitima__etnia='AM').count() + qs_mp.filter(vitima__etnia='AM').count(),
            qs_pm.filter(vitima__etnia='IN').count() + qs_pc.filter(vitima__etnia='IN').count() + qs_mp.filter(vitima__etnia='IN').count(),
        ]
    }
    
    # Classe Econômica
    classe_data = {
        "labels": ["Sem Renda", "Até R$1.518", "R$1.518-R$3.636", "R$3.636-R$7.018", "R$7.018-R$28.240", "Acima R$28.240"],
        "data": [
            qs_pm.filter(vitima__classeEconomica='SR').count() + qs_pc.filter(vitima__classeEconomica='SR').count() + qs_mp.filter(vitima__classeEconomica='SR').count(),
            qs_pm.filter(vitima__classeEconomica='AB').count() + qs_pc.filter(vitima__classeEconomica='AB').count() + qs_mp.filter(vitima__classeEconomica='AB').count(),
            qs_pm.filter(vitima__classeEconomica='BA').count() + qs_pc.filter(vitima__classeEconomica='BA').count() + qs_mp.filter(vitima__classeEconomica='BA').count(),
            qs_pm.filter(vitima__classeEconomica='BC').count() + qs_pc.filter(vitima__classeEconomica='BC').count() + qs_mp.filter(vitima__classeEconomica='BC').count(),
            qs_pm.filter(vitima__classeEconomica='BD').count() + qs_pc.filter(vitima__classeEconomica='BD').count() + qs_mp.filter(vitima__classeEconomica='BD').count(),
            qs_pm.filter(vitima__classeEconomica='AC').count() + qs_pc.filter(vitima__classeEconomica='AC').count() + qs_mp.filter(vitima__classeEconomica='AC').count(),
        ]
    }
    
    # Grau de Instrução
    grau_data = {
        "labels": ["Não Alfab.", "Fund. Inc.", "Fund. Comp.", "Médio Inc.", "Médio Comp.", "Sup. Inc.", "Sup. Comp.", "Pós-grad"],
        "data": [
            qs_pm.filter(vitima__escolaridade='AN').count() + qs_pc.filter(vitima__escolaridade='AN').count() + qs_mp.filter(vitima__escolaridade='AN').count(),
            qs_pm.filter(vitima__escolaridade='FI').count() + qs_pc.filter(vitima__escolaridade='FI').count() + qs_mp.filter(vitima__escolaridade='FI').count(),
            qs_pm.filter(vitima__escolaridade='FC').count() + qs_pc.filter(vitima__escolaridade='FC').count() + qs_mp.filter(vitima__escolaridade='FC').count(),
            qs_pm.filter(vitima__escolaridade='EI').count() + qs_pc.filter(vitima__escolaridade='EI').count() + qs_mp.filter(vitima__escolaridade='EI').count(),
            qs_pm.filter(vitima__escolaridade='EC').count() + qs_pc.filter(vitima__escolaridade='EC').count() + qs_mp.filter(vitima__escolaridade='EC').count(),
            qs_pm.filter(vitima__escolaridade='SU').count() + qs_pc.filter(vitima__escolaridade='SU').count() + qs_mp.filter(vitima__escolaridade='SU').count(),
            qs_pm.filter(vitima__escolaridade='SS').count() + qs_pc.filter(vitima__escolaridade='SS').count() + qs_mp.filter(vitima__escolaridade='SS').count(),
            qs_pm.filter(vitima__escolaridade='PO').count() + qs_pc.filter(vitima__escolaridade='PO').count() + qs_mp.filter(vitima__escolaridade='PO').count(),
        ]
    }
    
    # Parentesco
    parentesco_data = {
        "labels": ["Pai", "Tio", "Cônjuge", "Filho", "Cunhado", "Padrasto", "Outros"],
        "data": [
            qs_pm.filter(grau_parentesco_agressor='Pai').count() + qs_pc.filter(grau_parentesco_agressor='Pai').count() + qs_mp.filter(grau_parentesco_agressor='Pai').count(),
            qs_pm.filter(grau_parentesco_agressor='Tio').count() + qs_pc.filter(grau_parentesco_agressor='Tio').count() + qs_mp.filter(grau_parentesco_agressor='Tio').count(),
            qs_pm.filter(grau_parentesco_agressor='Conjuge').count() + qs_pc.filter(grau_parentesco_agressor='Conjuge').count() + qs_mp.filter(grau_parentesco_agressor='Conjuge').count(),
            qs_pm.filter(grau_parentesco_agressor='Filho').count() + qs_pc.filter(grau_parentesco_agressor='Filho').count() + qs_mp.filter(grau_parentesco_agressor='Filho').count(),
            qs_pm.filter(grau_parentesco_agressor='Cunhado').count() + qs_pc.filter(grau_parentesco_agressor='Cunhado').count() + qs_mp.filter(grau_parentesco_agressor='Cunhado').count(),
            qs_pm.filter(grau_parentesco_agressor='Padasto').count() + qs_pc.filter(grau_parentesco_agressor='Padasto').count() + qs_mp.filter(grau_parentesco_agressor='Padasto').count(),
            qs_pm.filter(grau_parentesco_agressor='Outros').count() + qs_pc.filter(grau_parentesco_agressor='Outros').count() + qs_mp.filter(grau_parentesco_agressor='Outros').count(),
        ]
    }
    
    # Comarcas com MP - CORRIGIDO: usar 'ID' maiúsculo para FormularioMedidaProtetiva
    comarcas_mp = qs_mp.values('comarca_competente__nome').annotate(
        total=Count('ID')  # Corrigido: 'ID' maiúsculo
    ).order_by('-total')
    
    comarcas_data = {
        "labels": [c['comarca_competente__nome'] or 'N/A' for c in comarcas_mp],
        "data": [c['total'] for c in comarcas_mp]
    }
    
    return {
        "violencia": {"labels": label_violencia, "data": dados_violencia},
        "idades": idades_data,
        "etnias": etnias_data,
        "classe": classe_data,
        "grau": grau_data,
        "parentesco": parentesco_data,
        "comarcas": comarcas_data,
    }




@checked_debug_decorador
def relatorios(request):
    """
    Renderiza a página de relatórios com dados estatísticos.
    Suporta HTMX para atualizações parciais.
    """
    
    # Aplicar filtros
    qs_pm, qs_pc, qs_mp, periodo_selecionado, comarca_selecionada = aplicar_filtros_queryset(request)
    
    # Verificar se é requisição HTMX
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    # Calcular dados dos gráficos
    dados_graficos = calcular_dados_graficos(qs_pm, qs_pc, qs_mp)
    
    # Tendência temporal (últimos 24 meses)
    tendencia_data = calcular_tendencia_temporal()
    
    # Estatísticas gerais
    try:
        dois_municipio = municipiosviolentos.municipios_mais_violentos(2)
        municipio_primeiro = dois_municipio[0][0]
        municipio_segundo = dois_municipio[1][0]
    except:
        municipio_primeiro = "N/A"
        municipio_segundo = "N/A"

    try:
        resultado_verifica = tipoviolencia.verifica_maior_violencia_por_mes()
        tipo_violencia_1 = resultado_verifica['mes_atual']['tipo']
        tipo_violencia_1_total = resultado_verifica['mes_atual']['total']
        tipo_violencia_1_porcentagem = resultado_verifica['mes_anterior']['porcentagem']
    except:
        tipo_violencia_1 = "N/A"
        tipo_violencia_1_total = 0
        tipo_violencia_1_porcentagem = 0

    try:
        medidas_protetivas_calculo = medidasprotetivas.porcentagem_mes_anterior()
        medidas_protetivas_solicitadas_ocorrencias = medidas_protetivas_calculo['total']
        medidas_protetivas_solicitadas_ocorrencias_porcentagem = medidas_protetivas_calculo['porcentagem']
    except:
        medidas_protetivas_solicitadas_ocorrencias = 0
        medidas_protetivas_solicitadas_ocorrencias_porcentagem = 0

    try:
        grau_parentesco_comum = grauparentesco.parentesco_mais_comum()['grau_parentesco']
    except:
        grau_parentesco_comum = "N/A"

    try:
        reincidencias = reincidencia.ocorrencias_reincidentes()
        val_count_porcentagem = reincidencias["reincidencia_agressor"]
        val_count = len(reincidencias["lista"])
    except:
        val_count_porcentagem = 0
        val_count = 0

    ano_atual = time.localtime().tm_year
    
    try:
        comarcas_pj = list(ComarcasPoderJudiciario.objects.values_list('nome', flat=True).order_by('nome'))
    except:
        comarcas_pj = []

    # Bairros para mapa
    bairros = [
        {"nome": "Novo Bairro", "lat": -26.771567, "lng": -53.190010, "casos": 10, "tipo_violencia": "Física"},
        {"nome": "Centro", "lat": -26.7670, "lng": -53.1850, "casos": 20, "tipo_violencia": "Psicológica"},
        {"nome": "Morada do Sol", "lat": -26.7690, "lng": -53.1700, "casos": 15, "tipo_violencia": "Sexual"},
        {"nome": "Padre Antonio", "lat": -26.7630, "lng": -53.1870, "casos": 25, "tipo_violencia": "Patrimonial"},
        {"nome": "Linha Sanga Silva", "lat": -26.73157, "lng": -53.19992, "casos": 1, "tipo_violencia": "Moral"},
    ]

    context = {
        "title": "Painel Informativo",
        "description": "Visualize o painel informativo estatístico gerados na plataforma.",
        "ano_atual": ano_atual,
        "periodo": ['Todos', 'Semanal', 'Mensal', 'Anual'],
        "periodo_selecionado": periodo_selecionado,
        "comarca_selecionada": comarca_selecionada,
        "comarcas": comarcas_pj,
        
        # Estatísticas
        "medidas_protetivas_solicitadas_ocorrencias_porcentagem": medidas_protetivas_solicitadas_ocorrencias_porcentagem,
        "medidas_protetivas_solicitadas_ocorrencias": medidas_protetivas_solicitadas_ocorrencias,
        "municipio_primeiro": municipio_primeiro,
        "municipio_segundo": municipio_segundo,
        "grau_parentesco_comum": grau_parentesco_comum,
        "reincidencia": val_count_porcentagem,
        "total_reincidencias": val_count,
        "tipo_violencia_1": tipo_violencia_1,
        "tipo_violencia_1_total": tipo_violencia_1_total,
        "tipo_violencia_1_porcentagem": tipo_violencia_1_porcentagem,
        
        # Dados para gráficos
        "tendencia_data": tendencia_data,
        "comarcas_com_mp": dados_graficos["comarcas"],
        "idades": dados_graficos["idades"],
        "etnias": dados_graficos["etnias"],
        "classeEconomica": dados_graficos["classe"],
        "grauInstrucao": dados_graficos["grau"],
        "parentesco_do_agressor": dados_graficos["parentesco"],
        "Tipos_de_Violência": dados_graficos["violencia"],
        
        # Mapa
        "bairros": bairros,
        
        # Cidades (estático por enquanto)
        "cidades": {
            "labels": ["Maravilha", "Tigrinhos", "Iraceminha"],
            "data": [50, 30, 20]
        },
    }
    
    # Se HTMX, retorna apenas os gráficos
    if is_htmx:
        return render(request, "partials/graficos_relatorios.html", context)
    
    return render(request, "relatorios.html", context)

@login_required
def api_tendencia_temporal(request):
    """
    Endpoint HTMX para retornar dados de tendência temporal filtrados
    """
    periodo = request.GET.get('periodo', 'Todos')
    comarca = request.GET.get('comarca', '')
    
    hoje = timezone.now()
    
    # Calcular data de início baseado no período
    if periodo == 'Semanal':
        data_inicio = hoje - timedelta(days=7)
        meses_total = 1
    elif periodo == 'Mensal':
        data_inicio = hoje.replace(day=1)
        meses_total = 1
    elif periodo == 'Anual':
        data_inicio = hoje.replace(month=1, day=1)
        meses_total = 12
    else:  # Todos
        data_inicio = hoje - timedelta(days=24*30)  # 24 meses
        meses_total = 24
    
    # Querysets base
    qs_pm = OcorrenciaMilitar.objects.filter(data_ocorrencia__gte=data_inicio)
    qs_pc = OcorrenciaCivil.objects.filter(data__gte=data_inicio)
    qs_mp = FormularioMedidaProtetiva.objects.filter(data_solicitacao__gte=data_inicio)
    
    # Aplicar filtro de comarca
    if comarca and comarca != 'Todas':
        qs_mp = qs_mp.filter(comarca_competente__nome=comarca)
        # OcorrenciaMilitar e OcorrenciaCivil podem não ter comarca
    
    # Agregar por mês usando TruncMonth
    from django.db.models.functions import TruncMonth
    
    dados_pm = qs_pm.annotate(
        mes_ano=TruncMonth('data_ocorrencia')
    ).values('mes_ano').annotate(
        total=Count('id')
    ).order_by('mes_ano')
    
    dados_pc = qs_pc.annotate(
        mes_ano=TruncMonth('data')
    ).values('mes_ano').annotate(
        total=Count('id')
    ).order_by('mes_ano')
    
    dados_mp = qs_mp.annotate(
        mes_ano=TruncMonth('data_solicitacao')
    ).values('mes_ano').annotate(
        total=Count('ID')
    ).order_by('mes_ano')
    
    # Consolidar dados
    todos_meses = {}
    
    for item in dados_pm:
        mes_key = item['mes_ano'].strftime('%Y-%m')
        todos_meses[mes_key] = todos_meses.get(mes_key, 0) + item['total']
    
    for item in dados_pc:
        mes_key = item['mes_ano'].strftime('%Y-%m')
        todos_meses[mes_key] = todos_meses.get(mes_key, 0) + item['total']
    
    for item in dados_mp:
        mes_key = item['mes_ano'].strftime('%Y-%m')
        todos_meses[mes_key] = todos_meses.get(mes_key, 0) + item['total']
    
    # Formatar para frontend
    meses_pt = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 
        5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    labels = []
    valores = []
    
    for mes_key in sorted(todos_meses.keys()):
        ano, mes = mes_key.split('-')
        label = f"{meses_pt[int(mes)]}/{ano[-2:]}"
        labels.append(label)
        valores.append(todos_meses[mes_key])
    
    return JsonResponse({
        'labels': labels,
        'data': valores,
        'total': sum(valores),
        'media': round(sum(valores) / len(valores), 1) if valores else 0
    })


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
    

@csrf_exempt
def chat_ia_publico(request):
    """Chat IA público para a página inicial, sem restrição de login."""
    if request.method == "POST":
        from sistema_justica.views.poder_judiciario import (
            verificar_ollama_disponivel, obter_resposta_ollama, obter_resposta_demo,
            OLLAMA_MODEL
        )
        from django.conf import settings

        pergunta = request.POST.get("mensagem", "").strip()
        if not pergunta:
            return HttpResponse("")

        USE_OLLAMA = getattr(settings, 'USE_OLLAMA', True)
        resposta_formatada = None
        usando_ollama = False

        if USE_OLLAMA and verificar_ollama_disponivel():
            resposta_formatada = obter_resposta_ollama(pergunta)
            if resposta_formatada:
                usando_ollama = True

        if not resposta_formatada:
            resposta_formatada = obter_resposta_demo(pergunta)

        fonte_resposta = ""
        if settings.DEBUG:
            if usando_ollama:
                fonte_resposta = f"<div class='text-xs text-green-600 mt-2'><i class='fas fa-robot mr-1'></i>Resposta gerada por IA local (Ollama - {OLLAMA_MODEL})</div>"
            else:
                fonte_resposta = "<div class='text-xs text-orange-600 mt-2'><i class='fas fa-info-circle mr-1'></i>Resposta pré-definida (Ollama indisponível)</div>"

        html_response = f"""
            <div class='flex justify-end mb-3'>
                <div class='bg-purple-600 text-white rounded-xl p-3 max-w-[80%] shadow-md'>
                    <p class='text-sm'>{pergunta}</p>
                </div>
            </div>
            <div class='flex items-start gap-2 mb-3'>
                <div class='w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center flex-shrink-0'>
                    <i class='fas fa-robot text-sm'></i>
                </div>
                <div class='bg-white rounded-xl p-4 max-w-[80%] shadow-md border border-gray-100'>
                    <p class='text-sm text-gray-700 leading-relaxed'>{resposta_formatada}</p>
                    {fonte_resposta}
                    <div class='mt-3 pt-3 border-t border-gray-200'>
                        <p class='text-xs text-gray-500'>
                            <i class='fas fa-phone-alt mr-1'></i>
                            Emergência: <strong>190</strong> | Central da Mulher: <strong>180</strong>
                        </p>
                    </div>
                </div>
            </div>
        """
        return HttpResponse(html_response)
    return HttpResponse("")