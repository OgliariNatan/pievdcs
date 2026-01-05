from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from sistema_justica.models.base import Vitima_dados, Agressor_dados
#from seguranca_publica.models.militar import RegistroMilitar

from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from usuarios.models import CustomUser
from django.contrib.auth.models import Group
from django.db.models import Count, Q, Prefetch
from django.utils import timezone


""" Configuraçao de decoradores para debug """
import os
from dotenv import load_dotenv

var_debug = os.getenv('DEBUG', False) #Carrega apenas a variavel de debug

if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
    
else:
    checked_debug_decorador = None
    checked_debug_decorador_fun = None

""" Fim da configuraçao de decoradores para debug """



@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
@checked_debug_decorador
def militar(request):
    notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)

    contexto = {
        'title': 'Polícia Militar',
        'encaminhamentos': 5,
        'alert': notificacoes_nao_lidas,
        'description': 'This page provides information about the militar system.',
        'user' : request.user,
    }
    return render(request, "militar.html", contexto)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
@checked_debug_decorador
def consultas_informacao_vitima_agressor(request):
    """Exibe todas as Medidas Protetivas com informações de vítimas e agressores"""
    
    # Buscar todas as medidas protetivas com relacionamentos
    medidas_protetivas = FormularioMedidaProtetiva.objects.select_related(
        'vitima',
        'agressor',
        'vitima__estado',
        'vitima__municipio',
        'agressor__estado',
        'agressor__municipio',
        'municipio_mp',
        'comarca_competente',
        #'tipo_de_violencia'
    ).prefetch_related(
        #Prefetch('vitima'),
        #Prefetch('agressor')
        'tipo_de_violencia'
    ).order_by('-data_solicitacao')
    
    # Estatísticas gerais
    total_medidas = medidas_protetivas.count()
    
    # Medidas deste mês
    hoje = timezone.now()
    medidas_mes = medidas_protetivas.filter(
        data_solicitacao__month=hoje.month,
        data_solicitacao__year=hoje.year
    ).count()
    
    # Contadores de vítimas e agressores únicos
    vitimas_unicas = medidas_protetivas.values('vitima__cpf').distinct().count()
    agressores_unicos = medidas_protetivas.values('agressor__cpf').distinct().count()
    
    # Adicionar contagem de medidas para cada vítima e agressor
    medidas_processadas = []
    for medida in medidas_protetivas:
        # Contar outras medidas da mesma vítima
        outras_medidas_vitima = FormularioMedidaProtetiva.objects.filter(
            vitima__cpf=medida.vitima.cpf
        ).exclude(ID=medida.ID).count()
        
        # Contar outras medidas do mesmo agressor
        outras_medidas_agressor = FormularioMedidaProtetiva.objects.filter(
            agressor__cpf=medida.agressor.cpf
        ).exclude(ID=medida.ID).count()
        
        medidas_processadas.append({
            'medida': medida,
            'outras_medidas_vitima': outras_medidas_vitima,
            'outras_medidas_agressor': outras_medidas_agressor
        })
    
    if var_debug == 'True':
        print(f"Total de Medidas Protetivas: {total_medidas}")
        print(f"Vítimas Únicas: {vitimas_unicas}")
        print(f"Agressores Únicos: {agressores_unicos}")
    
    context = {
        'title': 'Consultas de Medidas Protetivas',
        'description': 'Visualização completa de medidas protetivas com informações de vítimas e agressores',
        'user': request.user,
        'medidas_protetivas': medidas_processadas,
        'total_medidas': total_medidas,
        'medidas_mes': medidas_mes,
        'vitimas_unicas': vitimas_unicas,
        'agressores_unicos': agressores_unicos,
    }
    
    return render(request, "parcial/consultas_informacao_vitima_agressor.html", context)


@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
def buscar_vitimas(request):
    """
    View para busca de vítimas e agressores via HTMX. 
    Busca por nome ou CPF nas Medidas Protetivas.
    """
    query = request.GET.get('q', '').strip()
    
    if var_debug == 'True': 
        print(f"Solicitação de consulta:  '{query}'")
        print(f'Tamanho do query: {len(query)}')

    if len(query) < 2:
        return HttpResponse('''
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-info-circle text-2xl mb-2"></i>
                <p>Digite pelo menos 2 caracteres para buscar... </p>
            </div>
        ''')
    
    # Busca nas Medidas Protetivas por vítima OU agressor (nome ou CPF)
    medidas = FormularioMedidaProtetiva.objects. select_related(
        'vitima',
        'agressor',
        'vitima__estado',
        'vitima__municipio',
        'agressor__estado',
        'agressor__municipio',
    ).prefetch_related(
        'tipo_de_violencia'
    ).filter(
        # Busca por vítima
        Q(vitima__nome__icontains=query) | 
        Q(vitima__cpf__icontains=query) |
        # Busca por agressor
        Q(agressor__nome__icontains=query) | 
        Q(agressor__cpf__icontains=query)
    ).order_by('-data_solicitacao')[:20]  # Limita a 20 resultados
    
    if var_debug == 'True':
        print(f"Medidas encontradas: {medidas. count()}")
        for m in medidas: 
            print(f"  - Vítima: {m.vitima.nome} | Agressor: {m.agressor. nome} | data: {m.data_solicitacao}")
    
    if not medidas. exists():
        return HttpResponse('''
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-search text-2xl mb-2"></i>
                <p>Nenhum registro encontrado para essa busca. </p>
            </div>
        ''')
    
    # Processar resultados para indicar se a busca foi por vítima ou agressor
    resultados = []
    for medida in medidas: 
        # Verificar onde o termo foi encontrado
        encontrado_vitima = (
            query. lower() in medida.vitima.nome.lower() or 
            query.lower() in (medida.vitima.cpf or '').lower()
        )
        encontrado_agressor = (
            query. lower() in medida.agressor.nome.lower() or 
            query.lower() in (medida.agressor.cpf or '').lower()
        )
        
        resultados.append({
            'medida':  medida,
            'encontrado_vitima': encontrado_vitima,
            'encontrado_agressor': encontrado_agressor,
        })
    
    return render(request, 'seguranca_publica/parcial/resultados_busca_pm.html', {
        'resultados': resultados,
        'query':  query,
        'total': len(resultados)
    })