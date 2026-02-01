from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Count, Q, Prefetch
from django.utils import timezone
from collections import defaultdict
import os
from dotenv import load_dotenv

from .permission_group import grupos_permitidos
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from sistema_justica.models.base import Vitima_dados, Agressor_dados
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from usuarios.models import CustomUser
from django.contrib.auth.models import Group


""" Configuração de decoradores para debug """
var_debug = os.getenv('DEBUG', False)

if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
else:
    checked_debug_decorador = None
    checked_debug_decorador_fun = None


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
@checked_debug_decorador
def militar(request):
    """Página principal da Polícia Militar"""
    notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)

    contexto = {
        'title': 'Polícia Militar',
        'encaminhamentos': 5,
        'alert': notificacoes_nao_lidas,
        'description': 'Informações sobre o sistema da Polícia Militar',
        'user': request.user,
    }
    return render(request, "militar.html", contexto)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
@checked_debug_decorador
def consultas_informacao_vitima_agressor(request):
    """
    Carrega medidas protetivas com paginação infinita via HTMX.
    Suporta busca e filtros globais aplicados no backend.
    """
    
    # Captura parâmetros de busca e filtros
    busca = request.GET.get('busca', '').strip()
    status_filtro = request.GET.get('status', '')
    reincidencia_filtro = request.GET.get('reincidencia', '')
    ordenacao = request.GET.get('ordenacao', 'recente')
    
    if var_debug == 'True':
        print(f"🔍 Filtros aplicados: busca='{busca}', status='{status_filtro}', "
              f"reincidencia='{reincidencia_filtro}', ordenacao='{ordenacao}'")
    
    # Query base otimizada
    medidas_base = FormularioMedidaProtetiva.objects.select_related(
        'vitima',
        'agressor',
        'vitima__estado',
        'vitima__municipio',
        'agressor__estado',
        'agressor__municipio',
        'municipio_mp',
    ).prefetch_related('tipo_de_violencia')
    
    # Aplicar busca global (CPF ou nome)
    if busca:
        medidas_base = medidas_base.filter(
            Q(vitima__nome__icontains=busca) | 
            Q(vitima__cpf__icontains=busca) |
            Q(agressor__nome__icontains=busca) | 
            Q(agressor__cpf__icontains=busca)
        )
        
        if var_debug == 'True':
            print(f"📊 Registros após busca: {medidas_base.count()}")
    
    # Filtro de reincidência (agressor/vítima)
    if reincidencia_filtro == 'agressor':
        # Subquery: CPFs de agressores com mais de 1 medida
        agressores_reincidentes = FormularioMedidaProtetiva.objects.values(
            'agressor__cpf'
        ).annotate(
            total=Count('ID')
        ).filter(total__gt=1).values_list('agressor__cpf', flat=True)
        
        medidas_base = medidas_base.filter(agressor__cpf__in=list(agressores_reincidentes))
        
        if var_debug == 'True':
            print(f"🚨 Agressores reincidentes: {len(agressores_reincidentes)}")
            
    elif reincidencia_filtro == 'vitima':
        # Subquery: CPFs de vítimas com mais de 1 medida
        vitimas_recorrentes = FormularioMedidaProtetiva.objects.values(
            'vitima__cpf'
        ).annotate(
            total=Count('ID')
        ).filter(total__gt=1).values_list('vitima__cpf', flat=True)
        
        medidas_base = medidas_base.filter(vitima__cpf__in=list(vitimas_recorrentes))
        
        if var_debug == 'True':
            print(f"💜 Vítimas recorrentes: {len(vitimas_recorrentes)}")
    
    # Aplicar ordenação
    if ordenacao == 'recente':
        medidas_base = medidas_base.order_by('-data_solicitacao')
    elif ordenacao == 'antigo':
        medidas_base = medidas_base.order_by('data_solicitacao')
    elif ordenacao == 'prioridade':
        # Anotar com contagem de medidas por pessoa e ordenar
        medidas_base = medidas_base.annotate(
            total_agressor=Count('agressor__cpf', distinct=True),
            total_vitima=Count('vitima__cpf', distinct=True)
        ).order_by('-total_agressor', '-total_vitima', '-data_solicitacao')
    
    # Estatísticas FILTRADAS
    hoje = timezone.now()
    total_medidas_filtrado = medidas_base.count()
    medidas_mes_filtrado = medidas_base.filter(
        data_solicitacao__month=hoje.month,
        data_solicitacao__year=hoje.year
    ).count()
    vitimas_unicas_filtrado = medidas_base.values('vitima__cpf').distinct().count()
    agressores_unicos_filtrado = medidas_base.values('agressor__cpf').distinct().count()
    
    # Estatísticas GERAIS (sem filtros - apenas para comparação)
    if not any([busca, status_filtro, reincidencia_filtro]):
        total_geral = total_medidas_filtrado
        medidas_mes_geral = medidas_mes_filtrado
        vitimas_unicas_geral = vitimas_unicas_filtrado
        agressores_unicos_geral = agressores_unicos_filtrado
    else:
        total_geral = FormularioMedidaProtetiva.objects.count()
        medidas_mes_geral = FormularioMedidaProtetiva.objects.filter(
            data_solicitacao__month=hoje.month,
            data_solicitacao__year=hoje.year
        ).count()
        vitimas_unicas_geral = FormularioMedidaProtetiva.objects.values(
            'vitima__cpf'
        ).distinct().count()
        agressores_unicos_geral = FormularioMedidaProtetiva.objects.values(
            'agressor__cpf'
        ).distinct().count()
    
    # Paginação: 50 registros por página
    paginator = Paginator(medidas_base, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Processar apenas a página atual
    medidas_processadas = processar_medidas_pagina(page_obj)
    
    if var_debug == 'True':
        print(f"📄 Página: {page_number}/{paginator.num_pages}")
        print(f"📦 Registros na página: {len(medidas_processadas)}")
    
    # Requisição HTMX: retorna apenas os novos registros
    if request.headers.get('HX-Request'):
        return render(request, 'parcial/medidas_protetivas_lista.html', {
            'medidas_protetivas': medidas_processadas,
            'page_obj': page_obj,
        })
    
    # Requisição inicial: página completa com estatísticas
    context = {
        'title': 'Consultas de Medidas Protetivas',
        'description': 'Visualização de medidas protetivas com carregamento progressivo',
        'user': request.user,
        'medidas_protetivas': medidas_processadas,
        'page_obj': page_obj,
        # Estatísticas filtradas
        'total_medidas': total_medidas_filtrado,
        'medidas_mes': medidas_mes_filtrado,
        'vitimas_unicas': vitimas_unicas_filtrado,
        'agressores_unicos': agressores_unicos_filtrado,
        # Estatísticas gerais
        'total_geral': total_geral,
        'medidas_mes_geral': medidas_mes_geral,
        'vitimas_unicas_geral': vitimas_unicas_geral,
        'agressores_unicos_geral': agressores_unicos_geral,
        # Manter valores dos filtros nos inputs
        'filtro_busca': busca,
        'filtro_status': status_filtro,
        'filtro_reincidencia': reincidencia_filtro,
        'filtro_ordenacao': ordenacao,
    }
    
    return render(request, "parcial/consultas_informacao_vitima_agressor.html", context)


def processar_medidas_pagina(page_obj):
    """
    Processa medidas de uma página calculando contagens por CPF.
    Usa 'ID' maiúsculo conforme definição do modelo FormularioMedidaProtetiva.
    """
    cpfs_vitimas = [m.vitima.cpf for m in page_obj]
    cpfs_agressores = [m.agressor.cpf for m in page_obj]
    
    # Contagem em batch usando 'ID' (maiúsculo)
    contagem_vitimas = dict(
        FormularioMedidaProtetiva.objects.filter(
            vitima__cpf__in=cpfs_vitimas
        ).values('vitima__cpf').annotate(total=Count('ID')).values_list('vitima__cpf', 'total')
    )
    
    contagem_agressores = dict(
        FormularioMedidaProtetiva.objects.filter(
            agressor__cpf__in=cpfs_agressores
        ).values('agressor__cpf').annotate(total=Count('ID')).values_list('agressor__cpf', 'total')
    )
    
    # Monta lista processada
    medidas_processadas = []
    for medida in page_obj:
        # Calcula "outras medidas" excluindo a medida atual
        total_vitima = contagem_vitimas.get(medida.vitima.cpf, 0)
        total_agressor = contagem_agressores.get(medida.agressor.cpf, 0)
        
        medidas_processadas.append({
            'medida': medida,
            'outras_medidas_vitima': max(0, total_vitima - 1),
            'outras_medidas_agressor': max(0, total_agressor - 1),
        })
    
    return medidas_processadas

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
def buscar_vitimas(request):
    """
    Busca otimizada de vítimas e agressores via HTMX/AJAX.
    Retorna até 20 resultados mais recentes.
    """
    query = request.GET.get('q', '').strip()
    
    if var_debug == 'True':
        print(50 * '\033[33m-\033[0m')
        print(f"Solicitação de consulta: '{query}'")
        print(f'Tamanho do query: {len(query)}')
        print(f'Headers da requisição: {dict(request.headers)}')
        print(50 * '\033[33m-\033[0m')

    if len(query) < 2:
        context = {
            'resultados': [],
            'query': query,
            'total': 0,
            'mensagem': 'Digite pelo menos 2 caracteres para buscar...'
        }
        return render(request, 'parcial/resultados_busca_pm.html', context)
    
    # Query otimizada com limite de 20 resultados
    medidas = FormularioMedidaProtetiva.objects.select_related(
        'vitima',
        'agressor',
        'vitima__estado',
        'vitima__municipio',
        'agressor__estado',
        'agressor__municipio',
    ).prefetch_related(
        'tipo_de_violencia'
    ).filter(
        Q(vitima__nome__icontains=query) | 
        Q(vitima__cpf__icontains=query) |
        Q(agressor__nome__icontains=query) | 
        Q(agressor__cpf__icontains=query)
    ).order_by('-data_solicitacao')[:20]
    
    if var_debug == 'True':
        print(f"Medidas encontradas: {medidas.count()}")
        for m in medidas:
            print(f"  - Vítima: {m.vitima.nome} | Agressor: {m.agressor.nome} | Data: {m.data_solicitacao}")
    
    # Processar resultados identificando correspondências
    query_lower = query.lower()
    resultados = []
    
    for medida in medidas:
        encontrado_vitima = (
            query_lower in medida.vitima.nome.lower() or 
            query_lower in (medida.vitima.cpf or '').lower()
        )
        encontrado_agressor = (
            query_lower in medida.agressor.nome.lower() or 
            query_lower in (medida.agressor.cpf or '').lower()
        )
        
        resultados.append({
            'medida': medida,
            'encontrado_vitima': encontrado_vitima,
            'encontrado_agressor': encontrado_agressor,
        })

    if var_debug == 'True':
        print(50 * '\033[33m-\033[0m')
        print(f"Total de resultados processados: {len(resultados)}")
        print(f"Renderizando template com {len(resultados)} registros")
    
    context = {
        'resultados': resultados,
        'query': query,
        'total': len(resultados)
    }
    
    # Renderiza template completo
    response = render(request, 'parcial/resultados_busca_pm.html', context)
    
    if var_debug == 'True':
        print(f"✅ Resposta HTTP enviada com status {response.status_code}")
        print(f"Content-Type: {response.get('Content-Type')}")
        print(50 * '\033[33m-\033[0m')
    
    return response