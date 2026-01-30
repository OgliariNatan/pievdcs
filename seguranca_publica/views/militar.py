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
from collections import defaultdict


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
    """
    Exibe todas as Medidas Protetivas com informações de vítimas e agressores.
    Otimizado com agregação em memória em uma única passagem O(n).
    """
    
    # Query otimizada: carrega todos os dados relacionados em uma única consulta
    medidas_protetivas = FormularioMedidaProtetiva.objects.select_related(
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
    
    # Contadores usando defaultdict para performance
    contagem_vitimas = defaultdict(int)
    contagem_agressores = defaultdict(int)
    medidas_processadas = []
    
    # Data atual para filtro de mês
    hoje = timezone.now()
    medidas_mes_count = 0
    vitimas_cpf_set = set()
    agressores_cpf_set = set()
    
    # Processamento em ÚNICA PASSAGEM: O(n) ao invés de O(2n)
    for medida in medidas_protetivas:
        cpf_vitima = medida.vitima.cpf
        cpf_agressor = medida.agressor.cpf
        
        # Incrementa contadores
        contagem_vitimas[cpf_vitima] += 1
        contagem_agressores[cpf_agressor] += 1
        
        # Adiciona aos conjuntos de CPFs únicos
        vitimas_cpf_set.add(cpf_vitima)
        agressores_cpf_set.add(cpf_agressor)
        
        # Conta medidas do mês atual
        if (medida.data_solicitacao.month == hoje.month and 
            medida.data_solicitacao.year == hoje.year):
            medidas_mes_count += 1
        
        # Monta lista processada (não precisa iterar novamente)
        medidas_processadas.append({
            'medida': medida,
            'cpf_vitima': cpf_vitima,
            'cpf_agressor': cpf_agressor,
        })
    
    # Segunda passagem apenas para adicionar contagens (já calculadas)
    for item in medidas_processadas:
        item['outras_medidas_vitima'] = contagem_vitimas[item['cpf_vitima']] - 1
        item['outras_medidas_agressor'] = contagem_agressores[item['cpf_agressor']] - 1
        # Remove CPFs temporários (não necessários no template)
        del item['cpf_vitima']
        del item['cpf_agressor']
    
    # Estatísticas gerais
    total_medidas = len(medidas_processadas)
    vitimas_unicas = len(vitimas_cpf_set)
    agressores_unicos = len(agressores_cpf_set)
    
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
        'medidas_mes': medidas_mes_count,
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
        print((50*'\033[33m-\033[0m'))
        print(f"Solicitação de consulta:  '{query}'")
        print(f'Tamanho do query: {len(query)}')
        print(50*'\033[33m-\033[0m')

    if len(query) < 2:
        return HttpResponse('''
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-info-circle text-2xl mb-2"></i>
                <p>Digite pelo menos 2 caracteres para buscar... </p>
            </div>
        ''')
    
    # Busca nas Medidas Protetivas por vítima OU agressor (nome ou CPF)
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

    if var_debug == 'True':
        print(50*'\033[33m-\033[0m')
        print(f"Valor dos resultados processados:\t{resultados}")
        print(f"Total de resultados processados: {len(resultados)}")
    
    return render(request, 'parcial/resultados_busca_pm.html', {
        'resultados': resultados,
        'query':  query,
        'total': len(resultados)
    })