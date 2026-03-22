# -*- coding: utf-8 -*-
"""  
    Modelo pertinente as visualizações  publicas
    dir: MAIN/views.py
    @author: OgliariNatan
"""
import ollama
from argostranslate import translate
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.templatetags.static import static
from django.urls import reverse_lazy
from collections import defaultdict
from datetime import datetime, timedelta, date
from django.utils import timezone
from sistema_justica.models.base import Vitima_dados, TipoDeViolencia
from seguranca_publica.models.militar import OcorrenciaMilitar, AtendimentosRedeCatarina
from seguranca_publica.models.civil import OcorrenciaCivil
from seguranca_publica.models.penal import ModeloPenal
from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from municipio.models.creas import AtendimentoCREAS
from django.db import connection
from django.db.models import Prefetch, Count, Q
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear
from .models import ConteudoHome
from usuarios.models import CustomUser
from .calculo_variaveis import *
from collections import Counter
from rapidfuzz import fuzz
import requests as http_requests
import random
import time
import re
import unicodedata



# Configuração do Ollama
OLLAMA_HOST = getattr(settings, 'OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = getattr(settings, 'OLLAMA_MODEL', 'qwen2.5:7B')  # ou 'mixtral:latest', 'gemma3:27b', 'llama3.1:70b', 'llama3.1:latest', 'qwen3-vl:latest', 'gpt-oss:120b', 'qwen2.5:7B', 'deepseek-r1:32b'


def ANO_CORRENTE():
    return date.today().year

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
    
    
else:
    checked_debug_decorador = lambda x: x
    checked_debug_decorador_fun = lambda x: x
   

""" Fim da configuraçao de decoradores para debug """

_SPLIT_RE = re.compile(r"[;,/]|(?:\s+e\s+)|(?:\s+ou\s+)", flags=re.IGNORECASE)

_STOPWORDS = {
    "de", "da", "do", "das", "dos",
    "por", "para", "com", "sem",
    "a", "o", "as", "os", "um", "uma",
    "na", "no", "nas", "nos",
    "que", "em",
}


def _strip_accents(s: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", s)
        if unicodedata.category(ch) != "Mn"
    )


def _normalize_term(s: str) -> str:
    s = (s or "").strip().lower()
    s = _strip_accents(s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)  # tira pontuação
    s = re.sub(r"\s+", " ", s).strip()
    tokens = [t for t in s.split() if t not in _STOPWORDS]
    return " ".join(tokens)


def _extract_terms(text: str):
    parts = [p.strip() for p in _SPLIT_RE.split(text or "") if p and p.strip()]
    for p in parts:
        n = _normalize_term(p)
        if len(n) >= 3:
            yield n


def _canonicalize_fuzzy(term: str, canonicals: list, threshold: int = 86) -> str:
    """
    Retorna um termo canônico existente se for parecido o suficiente.
    Se rapidfuzz não estiver instalado, retorna o próprio termo.
    """
    if not canonicals or fuzz is None:
        return term

    best = None
    best_score = -1
    for c in canonicals:
        score = fuzz.token_sort_ratio(term, c)
        if score > best_score:
            best_score = score
            best = c

    if best is not None and best_score >= threshold:
        return best
    return term


def busca_causa():
    """
    Retorna string com as 3 'causas' mais frequentes (para card informativo),
    a partir de FormularioMedidaProtetiva.possivel_causa.

    - Multi-causa: "ciúmes e álcool" conta 1 para cada termo extraído.
    - Normaliza acento/pontuação.
    - Fuzzy (se rapidfuzz estiver instalado) junta erros comuns.
    """
    textos = (
        FormularioMedidaProtetiva.objects
        .exclude(Q(possivel_causa__isnull=True) | Q(possivel_causa__exact=''))
        .values_list('possivel_causa', flat=True)
    )

    counts = Counter()
    canonicals = []
    display = {}

    for raw in textos.iterator():
        for term in _extract_terms(raw):
            canon = _canonicalize_fuzzy(term, canonicals, threshold=86)

            # se for um canônico novo, registra
            if canon == term and canon not in canonicals:
                canonicals.append(canon)

            counts[canon] += 1
            # forma "bonita" para exibir
            display.setdefault(canon, canon.capitalize())

    top_terms = [display[t] for t, _ in counts.most_common(3)]

    causa1 = top_terms[0] if len(top_terms) > 0 else '—'
    causa2 = top_terms[1] if len(top_terms) > 1 else '—'
    causa3 = top_terms[2] if len(top_terms) > 2 else '—'

    
    return [causa1, causa2, causa3]


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
        grupos_atendidos = ModeloPenal.objects.all().count() + AtendimentoCREAS.objects.all().count()
    except Exception as e:
        if var_debug == 'True':
            print(f'Tipo de erro:{type(e).__name__}')
            print(f"Erro ao contar grupos atendidos: {e}")
        grupos_atendidos = 0

    try:
        casos_mediados = AtendimentosRedeCatarina.objects.values('id').count()
        
    except Exception as e:
        if var_debug == 'True':
            print(f'Tipo de erro:{type(e).__name__}')
            print(f"Erro ao contar casos mediados: {e}")
        casos_mediados = 0

    

    context = {
        "conteudos": conteudos,
        "title": "Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais",
        "description": "Página Inicial",
        'medidas_protetivas_solicitadas_ocorrencias': medidas_protetivas_solicitadas_ocorrencias,
        'ano_corrente': ANO_CORRENTE(),
        'encaminhamentos': grupos_atendidos,  # Criar variaveis para encaminhamentos
        'casos_mediados': casos_mediados,  # Criar variavel para casos mediados
        'atendimentos': casos_mediados + grupos_atendidos,
        'user': request.user,
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
        'ano_corrente': ANO_CORRENTE(),
        'user': request.user,
        
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
            print(f"\033[33mUsuário: {request.user}.\033[0m") 
            print(f"IP: {request.META.get('REMOTE_ADDR')}")
        raise PermissionError("Usuário inativo tentando acessar a página de notificações.")

    context = {
        "title": "Notificações",
        "description": "Visualize as notificações recebidas na plataforma.",
        'notificacao': [notificacoes],
        'user': request.user,
    }
    return render(request, "notificacoes.html", context)


def calcular_tendencia_temporal(comarca_filtrada=''):
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
    
    # Querysets base — sem filtro de período (tendência sempre exibe 24 meses)
    qs_pm_base = OcorrenciaMilitar.objects.all()
    qs_pc_base = OcorrenciaCivil.objects.all()
    qs_mp_base = FormularioMedidaProtetiva.objects.all()

    # Aplica filtro de comarca se informado
    if comarca_filtrada and comarca_filtrada != 'Todas':
        qs_mp_base = qs_mp_base.filter(comarca_competente__nome=comarca_filtrada)
        qs_pc_base = qs_pc_base.filter(
            Q(comarca_competente__nome=comarca_filtrada) | Q(comarca_competente__isnull=True)
        )

    for mes in meses:
        inicio = mes
        fim = mes.replace(year=mes.year + 1, month=1) if mes.month == 12 else mes.replace(month=mes.month + 1)

        count_pm = qs_pm_base.filter(data__gte=inicio, data__lt=fim).count()
        count_pc = qs_pc_base.filter(data__gte=inicio, data__lt=fim).count()
        count_mp = qs_mp_base.filter(data_solicitacao__gte=inicio, data_solicitacao__lt=fim).count()

        labels.append(f"{meses_pt[mes.month]}/{mes.year}")
        dados.append(count_pm + count_pc + count_mp)

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


def calcular_dados_graficos(qs_pm, qs_pc, qs_mp, comarca_filtrada=''):
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
    
    # Comarcas ou Municípios (depende do filtro ativo)
    if comarca_filtrada and comarca_filtrada != 'Todas':
        # Comarca selecionada → mostra distribuição por municípios da comarca
        agrupamento = qs_mp.values('municipio_mp__nome').annotate(
            total=Count('ID')
        ).order_by('-total')
        comarcas_data = {
            "labels": [c['municipio_mp__nome'] or 'N/A' for c in agrupamento],
            "data": [c['total'] for c in agrupamento],
            "titulo": f"Municípios — Comarca {comarca_filtrada}",
            "eixo_x": "Municípios",
        }
    else:
        # Sem filtro → mostra todas as comarcas
        agrupamento = qs_mp.values('comarca_competente__nome').annotate(
            total=Count('ID')
        ).order_by('-total')
        comarcas_data = {
            "labels": [c['comarca_competente__nome'] or 'N/A' for c in agrupamento],
            "data": [c['total'] for c in agrupamento],
            "titulo": "Distribuição por Comarcas",
            "eixo_x": "Comarcas",
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

def calcular_municipios_mapa(qs_pm, qs_pc, qs_mp):
    """
    Agrega ocorrências por município com limites geográficos e tipos de violência.
    Retorna lista de dicts prontos para serialização JSON no mapa Leaflet.
    """
    municipios = {}

    # PM e Civil usam municipio_ocorrencia (campo direto na OcorrenciaBase)
    for qs in [qs_pm, qs_pc]:
        resultados = (
            qs.filter(municipio_ocorrencia__limites__isnull=False)
            .values(
                'municipio_ocorrencia__id',
                'municipio_ocorrencia__nome',
                'municipio_ocorrencia__limites',
                'tipo_de_violencia__nome',
            )
            .annotate(total=Count('id'))
        )
        for r in resultados:
            mid = r['municipio_ocorrencia__id']
            if mid is None:
                continue
            if mid not in municipios:
                municipios[mid] = {
                    'id': mid,
                    'nome': r['municipio_ocorrencia__nome'],
                    'limites': r['municipio_ocorrencia__limites'],
                    'tipos': {},
                    'total': 0,
                }
            tipo = r['tipo_de_violencia__nome'] or 'Sem tipo'
            municipios[mid]['tipos'][tipo] = municipios[mid]['tipos'].get(tipo, 0) + r['total']
            municipios[mid]['total'] += r['total']

    # FormularioMedidaProtetiva usa municipio_mp
    resultados_mp = (
        # DEPOIS:
        qs_mp.filter(municipio_mp__limites__isnull=False)
        .values(
            'municipio_mp__id',
            'municipio_mp__nome',
            'municipio_mp__limites',
            'tipo_de_violencia__nome',
        )
        .annotate(total=Count('ID', distinct=True))
    )
    for r in resultados_mp:
        mid = r['municipio_mp__id']
        if mid is None:
            continue
        if mid not in municipios:
            municipios[mid] = {
                'id': mid,
                'nome': r['municipio_mp__nome'],
                'limites': r['municipio_mp__limites'],
                'tipos': {},
                'total': 0,
            }
        tipo = r['tipo_de_violencia__nome'] or 'Sem tipo'
        municipios[mid]['tipos'][tipo] = municipios[mid]['tipos'].get(tipo, 0) + r['total']
        municipios[mid]['total'] += r['total']

    # Determina o tipo dominante por município
    resultado = []
    for dados in municipios.values():
        dados['tipo_principal'] = (
            max(dados['tipos'], key=dados['tipos'].get)
            if dados['tipos'] else 'Sem registro'
        )
        resultado.append(dados)

    return resultado


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
    dados_graficos = calcular_dados_graficos(qs_pm, qs_pc, qs_mp, comarca_selecionada)
    
    # Tendência temporal (últimos 24 meses)
    tendencia_data = calcular_tendencia_temporal(comarca_selecionada)
    
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

    
    
    try:
        comarcas_pj = list(ComarcasPoderJudiciario.objects.values_list('nome', flat=True).order_by('nome'))
    except:
        comarcas_pj = []

    # Municípios com limites geográficos para o mapa
    municipios_mapa = calcular_municipios_mapa(qs_pm, qs_pc, qs_mp)
       

    try:
        busca_causa_resultado = busca_causa()
    except Exception as e:
        if var_debug == 'True':
            print(f'Erro ao buscar causas frequentes: {e}')
        busca_causa_resultado = "N/A"


    context = {
        "title": "Painel Informativo",
        "description": "Visualize o painel informativo estatístico gerados na plataforma.",
        'ano_corrente': ANO_CORRENTE(),
        "periodo": ['Todos', 'Semanal', 'Mensal', 'Anual'],
        "periodo_selecionado": periodo_selecionado,
        "comarca_selecionada": comarca_selecionada,
        "comarcas": comarcas_pj,
        'busca_causa_resultado': busca_causa_resultado,
        'user': request.user,
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
        'municipios_mapa': municipios_mapa,
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

    def form_valid(self, form):
        """Se 'manter conectado' marcado, sessão dura 30 dias; caso contrário, expira ao fechar."""
        remember_me = self.request.POST.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(60 * 60 * 24 * 30)  # 30 dias
        else:
            self.request.session.set_expiry(0)  # Expira ao fechar navegador
        return super().form_valid(form)


def verificar_ollama_disponivel():
    """Verifica se o Ollama está rodando e acessível"""
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        # Tenta listar modelos para verificar conexão
        models = client.list()
        if var_debug:
            nomes_modelos = [model['model'] for model in models['models']]
            print(f"\033[33mOllama está disponível. Modelos: {', '.join(nomes_modelos)}\033[0m")
        return True
    except Exception as e:
        print(f"Ollama não está disponível: {e}")
        return False

def obter_resposta_ollama(pergunta):
    """Obtém resposta do modelo Ollama"""
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        #print(f'cliente {client.list()}')
        # System prompt especializado para violência doméstica
        system_prompt = """Você é uma assistente especializada em casos de violência doméstica contra a mulher no Brasil.
        
        Suas responsabilidades incluem:
        - Fornecer informações sobre a Lei Maria da Penha (Lei 11.340/2006)
        - Orientar sobre medidas protetivas de urgência
        - Explicar direitos das vítimas de violência doméstica
        - Informar sobre procedimentos de denúncia
        - Indicar redes de apoio e acolhimento
        - Esclarecer sobre tipos de violência (física, psicológica, sexual, patrimonial, moral e Vicária)
        - Indicar caso necessário denuncia via Defensoria Publica ou na Delegacia Virtual(https://delegaciavirtual.sc.gov.br/nova-ocorrencia)

        Responda de forma clara, empática e acolhedora. Use linguagem simples e evite jargões jurídicos complexos.
        Sempre priorize a segurança da vítima e indique buscar ajuda profissional quando necessário.
        
        Não forneça conselhos médicos ou psicológicos específicos.
        Em casos urgentes, sempre recomende ligar para 190 (Polícia) ou 180 (Central de Atendimento à Mulher).
        Se tiver lesionada informe assistência médica, através do SAMU 192 ou no hospital mais próximo.
        Denúncias on-line no site da [Delegacia Virtual (Registro de BO)](https://delegaciavirtual.sc.gov.br/nova-ocorrencia).

        Quando solicitar uma conversa oriente a entrar em contato através do whatsapp para o número [554832872635](https://api.whatsapp.com/send?phone=554832872635), serviço do Tribunal de Justiça de Santa Catarina.

        [
        Quando citado o corte da pensão alimentícia, informe que se encaixa na violência vicária.
        Conceito de Violência Vicária:
        A violência vicária (ou violência por procuração) é uma forma grave de violência doméstica e de gênero, na qual o agressor (geralmente o ex-parceiro) utiliza uma terceira pessoa — predominantemente os filhos, mas também outros entes queridos ou animais de estimação — como "instrumento" ou "arma" para causar sofrimento e dano psicológico à vítima principal (a mulher).
        Pontos-chave a considerar:
        Objetivo Principal: O objetivo central não é a agressão direta à vítima principal, mas sim infligir a dor mais profunda e duradoura possível, atingindo o que ela mais ama ou valoriza.
        Instrumentalização: A vítima secundária (ex: o filho) é vista como um objeto ou meio para atingir a vítima principal.
        Contexto: Frequentemente ocorre em processos de separação litigiosa, disputas de guarda e após o término do relacionamento, quando o agressor perde o controle direto sobre a vítima.
        ]

        Formate suas respostas usando HTML básico:
        - Use <a href=""> para links
        - Use <strong> para destacar informações importantes
        - Use <br> para quebras de linha
        - Use <p> para parágrafos
        - Organize listas com • seguido de espaço
        - Evite usar listas numeradas

        Porque o nome de LaelIA?
        Laelia é um tipo de orquídea conhecida por sua beleza e resiliência, simbolizando a força e a delicadeza das mulheres que enfrentam a violência doméstica e simbolo oficial do estado de Santa Catarina. O nome LaelIA reflete a missão da assistente virtual de oferecer apoio, informação e empoderamento às vítimas, ajudando-as a florescer apesar das adversidades que enfrentam. Uma Curiosidade sobre o nome que possui o -IA- na composição do nome para destacar sua natureza de inteligência artificial.
        """
        
        # Cria o prompt completo
        prompt_completo = f"{system_prompt}\n\nUsuário: {pergunta}\n\nLaelIA:"
        
        # Faz a chamada ao Ollama
        response = client.generate(
            model=OLLAMA_MODEL,
            prompt=prompt_completo,
            system='Seu nome é Lael<b>IA</b>, uma assistente virtual especializada em violência doméstica contra a mulher no Brasil.',
            context=[1, 2, 3],  # Mantém o contexto das últimas interações
            stream=False,# Se True, recebe a resposta em partes (streaming)

            options={
                'temperature': 0.4,  # Baixo para respostas mais focadas 
                'num_predict': 800,  # tamanho da resposta
                'seed': None,
                'top_p': 0.7, # Inicial 0.9
                'top_k': 20,
                'repeat_penalty': 1.2,
                'num_ctx': 4096,
                #'stop': ['\n\nUsuário:', '\n\Laelia:', 'FIM'],
                'num_gpu':1,
                'mirostat': 2,
                'mirostat_tau': 5.0,
            },
            keep_alive='5m',
        )
        
        # Extrai a resposta
        resposta = response['response']
        
        # Formata a resposta para HTML
        resposta_formatada = resposta.replace('\n\n', '<br><br>').replace('\n', '<br>')
        
        # Adiciona formatação para listas
        linhas = resposta_formatada.split('<br>')
        linhas_formatadas = []
        for linha in linhas:
            if linha.strip().startswith('- '):
                linha = '• ' + linha.strip()[2:]
            linhas_formatadas.append(linha)
        resposta_formatada = '<br>'.join(linhas_formatadas)
        
        return resposta_formatada
        
    except Exception as e:
        print(f"Erro ao chamar Ollama: {e}")
        return None

def obter_resposta_demo(pergunta):
    """Respostas demo quando Ollama não está disponível"""
    pergunta_lower = pergunta.lower()
    
    if "medida protetiva" in pergunta_lower or "medidas protetivas" in pergunta_lower:
        return """A medida protetiva é um instrumento jurídico previsto na Lei Maria da Penha (Lei 11.340/2006) para proteger mulheres em situação de violência.
        <br><br><strong>Como solicitar:</strong>
        <br>• Procure a Defensoria Pública ou;
        <br>• Procure uma Delegacia da Mulher, Delegacia comum ou [Delegacia Virtual](https://delegaciavirtual.sc.gov.br/nova-ocorrencia).
        <br>• Relate os fatos e peça a medida protetiva
        <br>• Não é necessário advogado
        <br>• O juiz tem 48h para decidir
        <br><br><strong>O que pode incluir:</strong>
        <br>• Afastamento do agressor do lar
        <br>• Proibição de aproximação (mínimo 200m)
        <br>• Proibição de contato por qualquer meio
        <br>• Suspensão de porte de arma
        <br>• Prestação de alimentos provisórios"""
    
    elif "documento" in pergunta_lower or "documentos" in pergunta_lower:
        return """Para registrar uma denúncia de violência doméstica, você pode levar:
        <br><br><strong>Documentos úteis:</strong>
        <br>• RG e CPF (seus e do agressor, se tiver)
        <br>• Comprovante de residência
        <br>• Certidão de nascimento dos filhos
        <br>• Fotos de lesões ou danos
        <br>• Mensagens, e-mails ou áudios ameaçadores
        <br>• Laudos médicos (se houver)
        <br>• Boletins de ocorrência anteriores
        <br><br><strong>Importante:</strong> Mesmo sem documentos, você pode e deve denunciar! A palavra da vítima tem valor especial nos casos de violência doméstica."""
    
    elif "acolhimento" in pergunta_lower:
        return """O acolhimento de vítimas de violência doméstica funciona através de uma rede de proteção:
        <br><br><strong>Serviços disponíveis:</strong>
        <br>• <strong>Casa-abrigo:</strong> Local sigiloso e seguro para vítimas em risco
        <br>• <strong>Centro de Referência da Mulher:</strong> Atendimento psicológico, social e jurídico
        <br>• <strong>CRAS/CREAS:</strong> Assistência social e encaminhamentos
        <br>• <strong>Defensoria Pública:</strong> Assistência jurídica gratuita
        <br><br><strong>Como acessar:</strong>
        <br>• Ligue 180 (Central de Atendimento à Mulher)
        <br>• Procure a Delegacia da Mulher
        <br>• Vá ao CREAS mais próximo
        <br>• Busque o Centro de Referência da sua cidade"""
    
    elif "denunc" in pergunta_lower or "denúncia" in pergunta_lower:
        return """Para denunciar violência doméstica:
        <br><br><strong>Onde denunciar:</strong>
        <br>• <strong>Emergência:</strong> Ligue 190
        <br>• <strong>Central da Mulher:</strong> Ligue 180 (24h, gratuito)
        <br>• <strong>Delegacia da Mulher:</strong> Atendimento especializado
        <br>• <strong>Delegacia comum:</strong> Na ausência de delegacia especializada
        <br>• <strong>Delegacia Virtual:</strong> Registro de BO online
        <br>• <strong>Defensoria Pública:</strong> Assistência jurídica gratuita
        <br>• <strong>Ministério Público:</strong> Denúncias diretas
        <br>• <strong>Online:</strong> Alguns estados têm delegacia virtual
        <br><br><strong>Importante:</strong>
        <br>• A denúncia pode ser anônima pelo 180
        <br>• Vizinhos e familiares também podem denunciar
        <br>• Em caso de flagrante, a polícia deve prender o agressor"""
    
    elif "tipo" in pergunta_lower and "violência" in pergunta_lower:
        return """A Lei Maria da Penha reconhece 5 tipos de violência doméstica:
        <br><br><strong>1. Violência Física:</strong>
        <br>• Tapas, socos, empurrões, chutes
        <br>• Arremesso de objetos, queimaduras
        <br>• Uso de armas
        <br><br><strong>2. Violência Psicológica:</strong>
        <br>• Humilhações, xingamentos, ameaças
        <br>• Isolamento de amigos e familiares
        <br>• Controle excessivo
        <br><br><strong>3. Violência Sexual:</strong>
        <br>• Relação sexual forçada
        <br>• Impedir uso de contraceptivos
        <br>• Forçar aborto ou gravidez
        <br><br><strong>4. Violência Patrimonial:</strong>
        <br>• Destruir objetos pessoais
        <br>• Reter documentos
        <br>• Controlar dinheiro
        <br><br><strong>5. Violência Moral:</strong>
        <br>• Calúnia, difamação, injúria
        <br>• Expor a vida íntima"""
    
    elif "direito" in pergunta_lower:
        return """As vítimas de violência doméstica têm diversos direitos garantidos:
        <br><br><strong>Direitos principais:</strong>
        <br>• Atendimento prioritário e especializado
        <br>• Medidas protetivas de urgência
        <br>• Assistência jurídica gratuita
        <br>• Atendimento médico e psicológico
        <br>• Abrigamento sigiloso quando em risco
        <br>• Afastamento do trabalho por até 6 meses
        <br>• Prioridade para transferir matrícula escolar dos filhos
        <br>• Inclusão em programas sociais
        <br><br><strong>Na delegacia:</strong>
        <br>• Ser atendida por policial mulher (quando possível)
        <br>• Registrar ocorrência em local reservado
        <br>• Não ser questionada sobre sua vida íntima
        <br>• Receber cópia do B.O. imediatamente"""
    
    else:
        return f"""Entendo sua pergunta sobre: "<em>{pergunta}</em>"
        <br><br>Posso ajudar com informações sobre:
        <br>• <strong>Medidas protetivas</strong> - Como solicitar proteção judicial
        <br>• <strong>Documentos necessários</strong> - O que levar para denunciar
        <br>• <strong>Acolhimento</strong> - Rede de apoio disponível
        <br>• <strong>Tipos de violência</strong> - Física, psicológica, sexual, etc.
        <br>• <strong>Direitos da vítima</strong> - Garantias legais
        <br>• <strong>Como denunciar</strong> - Passo a passo
        <br><br>Por favor, seja mais específica ou escolha um dos tópicos acima."""




@checked_debug_decorador
@csrf_exempt
def chat_ia_publico(request):
    """Chat IA público para a página inicial, sem restrição de login."""
    if request.method == "POST":
       

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
        chat_bot_img_url = static('img/chat_bot.png')
        html_response = f"""
            <div class='flex justify-end mb-3'>
                <div class='bg-purple-600 text-white rounded-xl p-3 max-w-[80%] shadow-md'>
                    <p class='text-sm'>{pergunta}</p>
                </div>
            </div>
            <div class='flex items-start gap-2 mb-3'>
                <div class='w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center flex-shrink-0'>
                    <img src="{chat_bot_img_url}" alt="Assistente" class="w-7 h-7 object-contain">
                </div>
                <div class='bg-white rounded-xl p-4 max-w-[80%] shadow-md border border-gray-100'>
                    <p class='text-sm text-gray-700 leading-relaxed'>{resposta_formatada}</p>
                    {fonte_resposta}
                    <div class='mt-3 pt-3 border-t border-gray-200'>
                        <p class='text-xs text-gray-500'>
                            <i class='fas fa-phone-alt mr-1'></i>
                            Emergência: <strong>190</strong> | Central da Mulher: <strong>180</strong> <br>
                            <a href="https://api.whatsapp.com/send?phone=554832872635" target="_blank" class="ml-4 text-purple-400 hover:underline">
                                <i class="fab fa-whatsapp mr-1"></i>Atendimento de apoio via WhatsApp
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        """
        return HttpResponse(html_response)
    return HttpResponse("")

@login_required
def inserir_noticia_form(request):
    """Exibe popup com formulário para inserir notícia via HTMX."""
    from .forms import ConteudoHomeForm
    form = ConteudoHomeForm()
    return render(request, 'partials/inserir_noticia.html', {'form': form})


@login_required
def inserir_noticia_submit(request):
    """Processa o envio do formulário de notícia via HTMX."""
    from .forms import ConteudoHomeForm

    if request.method != 'POST':
        return HttpResponse(status=405)

    form = ConteudoHomeForm(request.POST, request.FILES)
    if form.is_valid():
        noticia = form.save(commit=False)
        noticia.autor = request.user
        noticia.save()
        # Retorna formulário limpo com aviso de sucesso
        form = ConteudoHomeForm()
        return render(request, 'partials/inserir_noticia.html', {
            'form': form,
            'enviado': True,
            'is_swap': True,
        })

    # Formulário com erros
    return render(request, 'partials/inserir_noticia.html', {
        'form': form,
        'is_swap': True,
    })

def popup_conteudo(request, pk):
    """Retorna popup com conteúdo completo de uma notícia via HTMX."""
    conteudo = get_object_or_404(ConteudoHome, pk=pk)
    return render(request, 'partials/popup_conteudo.html', {'conteudo': conteudo})

@login_required
def gerenciar_noticias(request):
    """Lista todas as notícias para gerenciamento via popup HTMX."""
    noticias = ConteudoHome.objects.select_related('autor').order_by('-data_publicacao')
    return render(request, 'partials/gerenciar_noticias.html', {'noticias': noticias})


@login_required
def editar_noticia(request, pk):
    """Exibe/processa edição de notícia via HTMX."""
    from .forms import ConteudoHomeForm

    noticia = get_object_or_404(ConteudoHome, pk=pk)

    if request.method == 'POST':
        form = ConteudoHomeForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save()
            form = ConteudoHomeForm(instance=noticia)
            return render(request, 'partials/editar_noticia.html', {
                'form': form,
                'noticia': noticia,
                'enviado': True,
                'is_swap': True,
            })
        return render(request, 'partials/editar_noticia.html', {
            'form': form,
            'noticia': noticia,
            'is_swap': True,
        })

    form = ConteudoHomeForm(instance=noticia)
    return render(request, 'partials/editar_noticia.html', {
        'form': form,
        'noticia': noticia,
    })


@login_required
def excluir_noticia(request, pk):
    """Exclui notícia e retorna lista atualizada via HTMX."""
    noticia = get_object_or_404(ConteudoHome, pk=pk)
    if request.method == 'DELETE' or request.method == 'POST':
        noticia.delete()
        noticias = ConteudoHome.objects.select_related('autor').order_by('-data_publicacao')
        return render(request, 'partials/gerenciar_noticias.html', {
            'noticias': noticias,
            'is_swap': True,
            'excluido': True,
        })
    return HttpResponse(status=405)


def frase_motivacional(request):
    """Proxy para a ZenQuotes API com tradução via MyMemory."""
    KEYWORDS = {
        'love': 'Amor',
        'confidence': 'Confiança',
        'courage': 'Coragem',
        'dreams': 'Sonhos',
        'freedom': 'Liberdade',
        'future': 'Futuro',
        'happiness': 'Felicidade',
        'inspiration': 'Inspiração',
        'life': 'Vida',
        'success': 'Sucesso',
        'time': 'Tempo',
    }

    FALLBACKS = [
        {'q': 'O segredo de avançar é começar.', 'a': 'Mark Twain', 'keyword_pt': 'Sucesso'},
        {'q': 'No meio de toda dificuldade existe uma oportunidade.', 'a': 'Albert Einstein', 'keyword_pt': 'Coragem'},
        {'q': 'A vida é o que acontece enquanto você está ocupado fazendo outros planos.', 'a': 'John Lennon', 'keyword_pt': 'Vida'},
        {'q': 'Espalhe amor por onde você for.', 'a': 'Madre Teresa', 'keyword_pt': 'Amor'},
        {'q': 'O futuro pertence àqueles que acreditam na beleza dos seus sonhos.', 'a': 'Eleanor Roosevelt', 'keyword_pt': 'Sonhos'},
    ]

    keyword_en = random.choice(list(KEYWORDS.keys()))
    keyword_pt = KEYWORDS[keyword_en]

    def traduzir(texto):
        """Traduz inglês → português via MyMemory (gratuita, sem chave)."""
        # try:
        #     url = f"https://api.mymemory.translated.net/get?q={texto}&langpair=en|pt-BR"
        #     resp = http_requests.get(url, timeout=4)
        #     resp.raise_for_status()
        #     data = resp.json()
        #     traducao = data.get('responseData', {}).get('translatedText', '')
        #     if traducao and data.get('responseStatus') == 200:
        #         return traducao
        # except Exception:
        #     pass
        # return texto  # Retorna original se falhar
        try:
            idiomas = translate.get_installed_languages()
            idioma_en = next((i for i in idiomas if i.code == "en"), None)
            idioma_pt = next((i for i in idiomas if i.code == "pt"), None)

            if not idioma_en or not idioma_pt:
                return texto

            traducao = idioma_en.get_translation(idioma_pt)
            return traducao.translate(texto)
        except Exception:
            return texto

    try:
        response = http_requests.get(
            'https://zenquotes.io/api/random',
            timeout=5,
            headers={'User-Agent': 'PIEVDCS/1.0'},
        )
        response.raise_for_status()
        data = response.json()
        quote = data[0]
        frase_traduzida = traduzir(quote['q'])
        return JsonResponse({
            'q': frase_traduzida,
            'a': quote['a'],
            'keyword_pt': keyword_pt,
        })
    except Exception:
        fallback = random.choice(FALLBACKS)
        return JsonResponse(fallback)

