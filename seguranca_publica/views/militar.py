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
    Performance otimizada: carrega apenas primeira página inicialmente.
    """
    
    # Query base otimizada
    medidas_base = FormularioMedidaProtetiva.objects.select_related(
        'vitima',
        'agressor',
        'vitima__estado',
        'vitima__municipio',
        'agressor__estado',
        'agressor__municipio',
        'municipio_mp',
    ).prefetch_related(
        'tipo_de_violencia'
    ).order_by('-data_solicitacao')
    
    # Estatísticas gerais (queries otimizadas)
    hoje = timezone.now()
    total_medidas = medidas_base.count()
    medidas_mes = medidas_base.filter(
        data_solicitacao__month=hoje.month,
        data_solicitacao__year=hoje.year
    ).count()
    vitimas_unicas = medidas_base.values('vitima__cpf').distinct().count()
    agressores_unicos = medidas_base.values('agressor__cpf').distinct().count()
    
    # Paginação: 50 registros por página
    paginator = Paginator(medidas_base, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Processar apenas a página atual
    medidas_processadas = processar_medidas_pagina(page_obj)
    
    if var_debug == 'True':
        print(f"Total de Medidas: {total_medidas}")
        print(f"Página: {page_number}/{paginator.num_pages}")
        print(f"Registros na página: {len(medidas_processadas)}")
    
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
        'total_medidas': total_medidas,
        'medidas_mes': medidas_mes,
        'vitimas_unicas': vitimas_unicas,
        'agressores_unicos': agressores_unicos,
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
        medidas_processadas.append({
            'medida': medida,
            'outras_medidas_vitima': contagem_vitimas.get(medida.vitima.cpf, 1) - 1,
            'outras_medidas_agressor': contagem_agressores.get(medida.agressor.cpf, 1) - 1,
        })
    
    return medidas_processadas


@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
def buscar_vitimas(request):
    """
    Busca otimizada de vítimas e agressores via HTMX.
    Retorna até 20 resultados mais recentes.
    """
    query = request.GET.get('q', '').strip()
    
    if var_debug == 'True':
        print(50 * '\033[33m-\033[0m')
        print(f"Solicitação de consulta: '{query}'")
        print(f'Tamanho do query: {len(query)}')
        print(50 * '\033[33m-\033[0m')

    if len(query) < 2:
        return HttpResponse('''
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-info-circle text-2xl mb-2"></i>
                <p>Digite pelo menos 2 caracteres para buscar...</p>
            </div>
        ''')
    
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
    
    if not medidas.exists():
        return HttpResponse('''
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-search text-2xl mb-2"></i>
                <p>Nenhum registro encontrado.</p>
            </div>
        ''')
    
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
    
    return render(request, 'parcial/resultados_busca_pm.html', {
        'resultados': resultados,
        'query': query,
        'total': len(resultados)
    })