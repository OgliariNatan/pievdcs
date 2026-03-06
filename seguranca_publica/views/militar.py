from django.conf import settings
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Count, Q, Prefetch
from django.utils import timezone
from collections import defaultdict
import os
import io
from datetime import datetime, date
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
from seguranca_publica.models.militar import AtendimentosRedeCatarina, AnexoAtendimento
from seguranca_publica.forms.atendimento_rede_catarina import AtendimentoRedeCatarinaForm, validar_anexos
from django.contrib.auth.models import Group
from .permission_group import grupos_permitidos
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from sistema_justica.models.base import Vitima_dados, Agressor_dados
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from usuarios.models import CustomUser
from django.contrib.auth.models import Group

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT

ANO_CORRENTE = timezone.now().year



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
    encaminhamentos_nao_lidos = Notificacao.contar_encaminhamentos_nao_lidos(request.user)

    contexto = {
        'title': 'Polícia Militar',
        'ano_corrente': ANO_CORRENTE,
        'encaminhamentos': encaminhamentos_nao_lidos,
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

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
def detalhe_medida_protetiva(request, medida_id):
    """Retorna o popup com detalhes completos da medida protetiva via HTMX."""
    medida = FormularioMedidaProtetiva.objects.select_related(
        'vitima', 'agressor',
        'vitima__estado', 'vitima__municipio',
        'agressor__estado', 'agressor__municipio',
        'comarca_competente', 'municipio_mp',
    ).prefetch_related(
        'tipo_de_violencia', 'filhos',
    ).get(ID=medida_id)

    return render(request, 'parcial/militar/detalhe_medida_protetiva.html', {
        'medida': medida,
    })


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
@checked_debug_decorador
def historico_mp_vitima(request, cpf_vitima):
    """
    Exibe histórico de MPs de uma vítima em popup autônomo.
    dir: seguranca_publica/views/militar.py
    """
    medidas = FormularioMedidaProtetiva.objects.filter(
        vitima__cpf=cpf_vitima
    ).select_related(
        'vitima', 'agressor',
        'vitima__estado', 'vitima__municipio',
        'agressor__estado', 'agressor__municipio',
    ).prefetch_related('tipo_de_violencia').order_by('-data_solicitacao')

    resultados = [
        {
            'medida': m,
            'encontrado_vitima': True,
            'encontrado_agressor': False,
        }
        for m in medidas
    ]

    nome = medidas.first().vitima.nome if medidas.exists() else cpf_vitima

    return render(request, 'parcial/militar/historico_mp_popup.html', {
        'resultados': resultados,
        'total': medidas.count(),
        'query': cpf_vitima,
        'titulo': f'Histórico da Vítima — {nome}',
        'cor_gradiente': 'from-purple-700 to-purple-500',
        'icone': 'fa-user-injured',
    })

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
@checked_debug_decorador
def historico_mp_agressor(request, cpf_agressor):
    """
    Exibe histórico de MPs de um agressor em popup autônomo.
    dir: seguranca_publica/views/militar.py
    """
    medidas = FormularioMedidaProtetiva.objects.filter(
        agressor__cpf=cpf_agressor
    ).select_related(
        'vitima', 'agressor',
        'vitima__estado', 'vitima__municipio',
        'agressor__estado', 'agressor__municipio',
    ).prefetch_related('tipo_de_violencia').order_by('-data_solicitacao')

    resultados = [
        {
            'medida': m,
            'encontrado_vitima': False,
            'encontrado_agressor': True,
        }
        for m in medidas
    ]

    nome = medidas.first().agressor.nome if medidas.exists() else cpf_agressor

    return render(request, 'parcial/militar/historico_mp_popup.html', {
        'resultados': resultados,
        'total': medidas.count(),
        'query': cpf_agressor,
        'titulo': f'Histórico do Agressor — {nome}',
        'cor_gradiente': 'from-orange-600 to-orange-400',
        'icone': 'fa-user-slash',
    })


# =============================================================================
# Views de Atendimentos da Rede Catarina
# =============================================================================

def _notificar_descumprimento(atendimento):
    """Envia notificação de descumprimento para autoridades competentes."""
    mp = atendimento.medida_protetiva
    vitima_nome = mp.vitima.nome if mp.vitima else "N/I"
    agressor_nome = mp.agressor.nome if mp.agressor else "N/I"

    titulo = f"⚠️ Descumprimento de Medida Protetiva - MP #{mp.ID}"
    mensagem = (
        f"Descumprimento relatado durante atendimento da Rede Catarina.\n\n"
        f"Medida Protetiva: #{mp.ID}\n"
        f"Vítima: {vitima_nome}\n"
        f"Agressor: {agressor_nome}\n"
        f"Data: {atendimento.data_atendimento.strftime('%d/%m/%Y %H:%M')}\n"
        f"Situação da vítima: {atendimento.get_situacao_vitima_display()}\n"
        f"Agressor presente: {'Sim' if atendimento.agressor_presente else 'Não'}\n\n"
        f"Descrição: {atendimento.descricao_descumprimento or 'Não informada'}\n"
        f"Providências: {atendimento.providencias_tomadas or 'Não informadas'}"
    )

    grupos_alvo = ['Poder Judiciário', 'Ministério Público', 'Defensoria Pública']
    for nome_grupo in grupos_alvo:
        try:
            grupo = Group.objects.get(name=nome_grupo)
            enviar_notificacao_grupo(
                request=None,
                grupo_destinatario=grupo,
                titulo=titulo,
                mensagem=mensagem,
                tipo='DESCUMPRIMENTO',
                prioridade='URGENTE',
                importante=True,
                remetente=atendimento.responsavel,
            )
        except Group.DoesNotExist:
            continue



def _salvar_anexos(imagens_validas, videos_validos, atendimento):
    """Salva imagens e vídeos já validados no banco."""
    for arq in imagens_validas:
        AnexoAtendimento.objects.create(
            atendimento=atendimento,
            tipo='imagem',
            imagem=arq,
        )
    for arq in videos_validos:
        AnexoAtendimento.objects.create(
            atendimento=atendimento,
            tipo='video',
            video=arq,
        )

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
def cadastrar_atendimento(request, medida_id):
    """Cadastra atendimento da Rede Catarina com anexos de imagem e vídeo."""
    medida = get_object_or_404(FormularioMedidaProtetiva, ID=medida_id)

    if request.method == 'POST':
        form = AtendimentoRedeCatarinaForm(request.POST)
        imagens_validas, videos_validos, erros_anexos = validar_anexos(request)

        if form.is_valid() and not erros_anexos:
            atendimento = form.save(commit=False)
            atendimento.medida_protetiva = medida
            atendimento.responsavel = request.user
            atendimento.save()

            _salvar_anexos(imagens_validas, videos_validos, atendimento)

            descumprimento_notificado = False
            if atendimento.vitima_relatou_descumprimento:
                _notificar_descumprimento(atendimento)
                atendimento.notificacao_enviada = True
                atendimento.save(update_fields=['notificacao_enviada'])
                descumprimento_notificado = True

            return render(request, 'parcial/militar/cadastrar_atendimento.html', {
                'form': AtendimentoRedeCatarinaForm(),
                'medida': medida,
                'enviado': True,
                'descumprimento_notificado': descumprimento_notificado,
                'is_swap': True,
            })

        return render(request, 'parcial/militar/cadastrar_atendimento.html', {
            'form': form,
            'medida': medida,
            'erros_anexos': erros_anexos,
            'is_swap': True,
        })

    return render(request, 'parcial/militar/cadastrar_atendimento.html', {
        'form': AtendimentoRedeCatarinaForm(),
        'medida': medida,
    })



@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
def listar_atendimentos(request, medida_id):
    """Lista atendimentos com anexos de uma medida protetiva."""
    medida = get_object_or_404(FormularioMedidaProtetiva, ID=medida_id)
    atendimentos = AtendimentosRedeCatarina.objects.filter(
        medida_protetiva=medida
    ).select_related('responsavel').prefetch_related('anexos').order_by('-data_atendimento')

    return render(request, 'parcial/militar/listar_atendimento.html', {
        'medida': medida,
        'atendimentos': atendimentos,
    })


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
def editar_atendimento(request, atendimento_id):
    """Edita atendimento existente e permite adicionar novos anexos."""
    atendimento = get_object_or_404(
        AtendimentosRedeCatarina.objects.prefetch_related('anexos'),
        id=atendimento_id,
    )
    medida = atendimento.medida_protetiva

    if request.method == 'POST':
        form = AtendimentoRedeCatarinaForm(request.POST, instance=atendimento)
        imagens_validas, videos_validos, erros_anexos = validar_anexos(request)

        if form.is_valid() and not erros_anexos:
            atendimento = form.save()
            _salvar_anexos(imagens_validas, videos_validos, atendimento)

            if atendimento.vitima_relatou_descumprimento and not atendimento.notificacao_enviada:
                _notificar_descumprimento(atendimento)
                atendimento.notificacao_enviada = True
                atendimento.save(update_fields=['notificacao_enviada'])

            atendimento.refresh_from_db()
            return render(request, 'parcial/militar/editar_atendimento.html', {
                'form': AtendimentoRedeCatarinaForm(instance=atendimento),
                'atendimento': atendimento,
                'medida': medida,
                'enviado': True,
                'is_swap': True,
            })

        return render(request, 'parcial/militar/editar_atendimento.html', {
            'form': form,
            'atendimento': atendimento,
            'medida': medida,
            'erros_anexos': erros_anexos,
            'is_swap': True,
        })

    return render(request, 'parcial/militar/editar_atendimento.html', {
        'form': AtendimentoRedeCatarinaForm(instance=atendimento),
        'atendimento': atendimento,
        'medida': medida,
    })



@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
def excluir_anexo_atendimento(request, anexo_id):
    """Exclui um anexo (imagem ou vídeo) de atendimento via HTMX."""
    anexo = get_object_or_404(AnexoAtendimento, id=anexo_id)
    atendimento = anexo.atendimento

    if request.method == 'DELETE':
        # Remove arquivo do disco
        if anexo.tipo == 'imagem' and anexo.imagem:
            anexo.imagem.delete(save=False)
        elif anexo.tipo == 'video' and anexo.video:
            anexo.video.delete(save=False)
        anexo.delete()

    atendimento.refresh_from_db()
    return render(request, 'parcial/militar/galeria_anexos.html', {
        'atendimento': atendimento,
        'anexos': atendimento.anexos.all(),
        'pode_excluir': True,
    })


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Militar'])
def relatorio_atendimentos_pdf(request, medida_id):
    """Gera relatório PDF dos atendimentos no formato de ofício institucional."""

    medida = get_object_or_404(FormularioMedidaProtetiva, ID=medida_id)
    atendimentos = AtendimentosRedeCatarina.objects.filter(
        medida_protetiva=medida
    ).select_related('responsavel').prefetch_related('anexos').order_by('data_atendimento')

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=3 * cm, rightMargin=2 * cm,
        topMargin=2.5 * cm, bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    agora = timezone.localtime(timezone.now())

    # === Estilos ===
    estilo_cabecalho = ParagraphStyle(
        'Cabecalho', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12,
        alignment=TA_CENTER, spaceAfter=2,
        textColor=colors.HexColor('#1e3a5f'),
    )
    estilo_subcabecalho = ParagraphStyle(
        'SubCabecalho', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10,
        alignment=TA_CENTER, textColor=colors.HexColor('#4a4a4a'),
    )
    estilo_subtitulo_cab = ParagraphStyle(
        'SubtituloCab', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8,
        alignment=TA_CENTER, textColor=colors.gray, spaceAfter=6,
    )
    estilo_assunto = ParagraphStyle(
        'Assunto', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10,
        alignment=TA_CENTER, spaceAfter=4,
        textColor=colors.HexColor('#1e3a5f'),
    )
    estilo_corpo = ParagraphStyle(
        'Corpo', parent=styles['Normal'],
        fontSize=11, alignment=TA_JUSTIFY,
        firstLineIndent=2 * cm, spaceAfter=10, leading=16,
    )
    estilo_corpo_sem_recuo = ParagraphStyle(
        'CorpoSemRecuo', parent=styles['Normal'],
        fontSize=11, alignment=TA_JUSTIFY,
        firstLineIndent=0, spaceAfter=10, leading=16,
    )
    estilo_secao = ParagraphStyle(
        'Secao', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9,
        textColor=colors.HexColor('#1e3a5f'),
        spaceAfter=6, spaceBefore=12,
    )
    estilo_assinatura = ParagraphStyle(
        'Assinatura', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10,
        alignment=TA_CENTER,
    )
    estilo_cargo = ParagraphStyle(
        'Cargo', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8,
        alignment=TA_CENTER, textColor=colors.gray,
    )
    estilo_rodape = ParagraphStyle(
        'Rodape', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7,
        alignment=TA_CENTER, textColor=colors.HexColor('#999999'),
    )
    estilo_celula = ParagraphStyle(
        'CelulaTabela', fontName='Helvetica', fontSize=8, leading=10,
    )
    estilo_alerta = ParagraphStyle(
        'Alerta', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=6, spaceBefore=8,
    )
    estilo_anexo_titulo = ParagraphStyle(
        'AnexoTitulo', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=4, spaceBefore=8,
    )
    estilo_anexo_desc = ParagraphStyle(
        'AnexoDesc', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER, spaceAfter=4,
    )
    estilo_video_ref = ParagraphStyle(
        'VideoRef', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8,
        textColor=colors.HexColor('#7c3aed'),
        spaceAfter=4,
    )

    elementos = []

    # === Cabeçalho institucional ===
    elementos.append(Paragraph(
        'PLATAFORMA INTEGRADA DE ENFRENTAMENTO À VIOLÊNCIA<br/>'
        'DOMÉSTICA E CRIMES SEXUAIS',
        estilo_cabecalho,
    ))
    elementos.append(Paragraph(
        'Polícia Militar — Rede Catarina de Proteção à Mulher',
        estilo_subcabecalho,
    ))
    elementos.append(Paragraph(
        'PIEVDCS — Sistema de Gestão Integrada',
        estilo_subtitulo_cab,
    ))
    elementos.append(HRFlowable(
        width='100%', thickness=2,
        color=colors.HexColor('#1e3a5f'), spaceAfter=20,
    ))

    # === Identificação do ofício ===
    meses = {
        'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
        'April': 'abril', 'May': 'maio', 'June': 'junho',
        'July': 'julho', 'August': 'agosto', 'September': 'setembro',
        'October': 'outubro', 'November': 'novembro', 'December': 'dezembro',
    }
    data_str = agora.strftime('%d de %B de %Y')
    for eng, pt in meses.items():
        data_str = data_str.replace(eng, pt)

    estilo_id_esq = ParagraphStyle(
        'IdEsq', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11,
        textColor=colors.HexColor('#1e3a5f'),
    )
    estilo_id_dir = ParagraphStyle(
        'IdDir', parent=styles['Normal'],
        fontSize=10, alignment=TA_RIGHT,
    )

    tabela_id = Table(
        [[
            Paragraph(
                f'OFÍCIO Nº {medida.ID}/{agora.strftime("%Y")}',
                estilo_id_esq,
            ),
            Paragraph(data_str, estilo_id_dir),
        ]],
        colWidths=[8 * cm, 7.7 * cm],
    )
    tabela_id.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementos.append(tabela_id)
    elementos.append(Spacer(1, 12))

    # === Assunto ===
    elementos.append(HRFlowable(
        width='100%', thickness=0.5, color=colors.HexColor('#ddd'),
        spaceBefore=0, spaceAfter=4,
    ))
    elementos.append(Paragraph(
        f'ASSUNTO: Relatório de Atendimentos da Rede Catarina — '
        f'Medida Protetiva nº {medida.ID}',
        estilo_assunto,
    ))
    elementos.append(HRFlowable(
        width='100%', thickness=0.5, color=colors.HexColor('#ddd'),
        spaceBefore=0, spaceAfter=16,
    ))

    # === Dados da Medida Protetiva ===
    vitima_nome = medida.vitima.nome if medida.vitima else "N/I"
    agressor_nome = medida.agressor.nome if medida.agressor else "N/I"
    vitima_cpf = medida.vitima.cpf if medida.vitima else "N/I"
    agressor_cpf = medida.agressor.cpf if medida.agressor else "N/I"

    elementos.append(Paragraph('DADOS DA MEDIDA PROTETIVA', estilo_secao))

    dados_mp = [
        ['Nº da Medida Protetiva:', str(medida.ID)],
        ['Vítima:', vitima_nome],
        ['CPF da Vítima:', vitima_cpf],
        ['Agressor:', agressor_nome],
        ['CPF do Agressor:', agressor_cpf],
    ]
    if hasattr(medida, 'data_solicitacao') and medida.data_solicitacao:
        dados_mp.append([
            'Data da Solicitação:',
            medida.data_solicitacao.strftime('%d/%m/%Y'),
        ])
    if hasattr(medida, 'periodo_mp') and medida.periodo_mp:
        dados_mp.append([
            'Vigência até:',
            medida.periodo_mp.strftime('%d/%m/%Y'),
        ])

    t_mp = Table(dados_mp, colWidths=[5.5 * cm, 10.2 * cm])
    t_mp.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#eeeeee')),
    ]))
    elementos.append(t_mp)
    elementos.append(Spacer(1, 16))

    # === Corpo do ofício ===
    qtd = atendimentos.count()
    qtd_descumprimentos = atendimentos.filter(
        vitima_relatou_descumprimento=True
    ).count()

    elementos.append(Paragraph(
        f'Comunicamos, para os devidos fins, que a Medida Protetiva de '
        f'nº <b>{medida.ID}</b>, em favor da vítima <b>{vitima_nome}</b>, '
        f'CPF <b>{vitima_cpf}</b>, em desfavor do agressor <b>{agressor_nome}</b>, '
        f'CPF <b>{agressor_cpf}</b>, possui <b>{qtd}</b> atendimento(s) '
        f'registrado(s) pela Rede Catarina de Proteção à Mulher.',
        estilo_corpo,
    ))

    if qtd_descumprimentos > 0:
        elementos.append(Paragraph(
            f'⚠ ATENÇÃO: Foram registrados <b>{qtd_descumprimentos}</b> '
            f'relato(s) de descumprimento da medida protetiva.',
            estilo_alerta,
        ))

    elementos.append(Spacer(1, 8))

    # === Tabela resumo dos atendimentos ===
    elementos.append(Paragraph('HISTÓRICO DE ATENDIMENTOS', estilo_secao))

    if atendimentos.exists():
        cabecalho = ['#', 'Data', 'Equipe', 'Contato', 'Agressor', 'Situação', 'Descumpr.', 'Anexos']
        dados_tabela = [cabecalho]

        for i, a in enumerate(atendimentos, 1):
            # Contar anexos por tipo
            anexos_atend = a.anexos.all()
            qtd_imgs = sum(1 for x in anexos_atend if x.tipo == 'imagem')
            qtd_vids = sum(1 for x in anexos_atend if x.tipo == 'video')
            anexos_txt = []
            if qtd_imgs:
                anexos_txt.append(f'{qtd_imgs} img')
            if qtd_vids:
                anexos_txt.append(f'{qtd_vids} víd')
            anexos_str = ', '.join(anexos_txt) if anexos_txt else '—'

            dados_tabela.append([
                str(i),
                a.data_atendimento.strftime('%d/%m/%Y %H:%M'),
                Paragraph(a.equipe or '—', estilo_celula),
                'Sim' if a.houve_contato_vitima else 'Não',
                'Sim' if a.agressor_presente else 'Não',
                Paragraph(a.get_situacao_vitima_display(), estilo_celula),
                'SIM' if a.vitima_relatou_descumprimento else 'Não',
                Paragraph(anexos_str, estilo_celula),
            ])

        t_atend = Table(
            dados_tabela,
            colWidths=[0.7 * cm, 2.7 * cm, 2.4 * cm, 1.5 * cm, 1.5 * cm, 2.4 * cm, 2 * cm, 2.5 * cm],
        )
        t_atend.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
                colors.white, colors.HexColor('#f9f9f9'),
            ]),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ]))
        elementos.append(t_atend)
        elementos.append(Spacer(1, 12))

        # === Detalhes individuais de cada atendimento ===
        elementos.append(Paragraph('DETALHAMENTO DOS ATENDIMENTOS', estilo_secao))

        for i, a in enumerate(atendimentos, 1):
            data_fmt = a.data_atendimento.strftime('%d/%m/%Y %H:%M')
            tipo_txt = a.get_tipo_patrulha_display() if a.tipo_patrulha else '—'
            responsavel = (
                a.responsavel.get_full_name() if a.responsavel else '—'
            )

            elementos.append(Paragraph(
                f'<b>Atendimento nº {i} — {data_fmt}</b>',
                estilo_corpo_sem_recuo,
            ))

            # Tabela de dados do atendimento
            dados_detalhe = [
                ['Tipo de Patrulha:', tipo_txt],
                ['Equipe/Viatura:', a.equipe or '—'],
                ['Contato com a vítima:', 'Sim' if a.houve_contato_vitima else 'Não'],
                ['Situação da vítima:', a.get_situacao_vitima_display()],
                ['Agressor presente:', 'Sim' if a.agressor_presente else 'Não'],
                ['Responsável:', responsavel],
            ]

            t_det = Table(dados_detalhe, colWidths=[5 * cm, 10.7 * cm])
            t_det.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#eeeeee')),
            ]))
            elementos.append(t_det)
            elementos.append(Spacer(1, 6))

            # Descrição do atendimento
            if a.descricao_atendimento:
                elementos.append(Paragraph(
                    f'<b>Descrição:</b> {a.descricao_atendimento}',
                    estilo_corpo_sem_recuo,
                ))

            # Descumprimento (destaque)
            if a.vitima_relatou_descumprimento:
                elementos.append(Paragraph(
                    f'⚠ <b>DESCUMPRIMENTO RELATADO:</b> '
                    f'{a.descricao_descumprimento or "Sem detalhes informados"}',
                    estilo_alerta,
                ))
                notif_txt = 'Sim' if a.notificacao_enviada else 'Não'
                elementos.append(Paragraph(
                    f'<b>Notificação enviada às autoridades:</b> {notif_txt}',
                    estilo_corpo_sem_recuo,
                ))

            # Providências
            if a.providencias_tomadas:
                elementos.append(Paragraph(
                    f'<b>Providências tomadas:</b> {a.providencias_tomadas}',
                    estilo_corpo_sem_recuo,
                ))

            # === ANEXOS DO ATENDIMENTO ===
            anexos_atend = a.anexos.all()
            imagens_anexo = [x for x in anexos_atend if x.tipo == 'imagem']
            videos_anexo = [x for x in anexos_atend if x.tipo == 'video']

            if imagens_anexo or videos_anexo:
                elementos.append(Paragraph(
                    f'ANEXOS DO ATENDIMENTO Nº {i}',
                    estilo_anexo_titulo,
                ))

                # Inserir imagens no PDF
                if imagens_anexo:
                    elementos.append(Paragraph(
                        f'Imagens anexadas ({len(imagens_anexo)}):',
                        estilo_anexo_titulo,
                    ))

                    # Agrupar imagens em linhas de 3
                    linha_imgs = []
                    for idx_img, img_anexo in enumerate(imagens_anexo):
                        try:
                            caminho = os.path.join(
                                settings.MEDIA_ROOT,
                                str(img_anexo.imagem),
                            )
                            if os.path.exists(caminho):
                                rl_img = RLImage(
                                    caminho,
                                    width=4.5 * cm,
                                    height=3.5 * cm,
                                )
                                desc_txt = img_anexo.descricao or f'Imagem {idx_img + 1}'
                                celula = [rl_img, Paragraph(desc_txt, estilo_anexo_desc)]
                                linha_imgs.append(celula)

                                # A cada 3 imagens ou na última, criar tabela
                                if len(linha_imgs) == 3 or idx_img == len(imagens_anexo) - 1:
                                    # Preencher com células vazias se necessário
                                    while len(linha_imgs) < 3:
                                        linha_imgs.append(['', ''])

                                    t_imgs = Table(
                                        [
                                            [c[0] for c in linha_imgs],
                                            [c[1] for c in linha_imgs],
                                        ],
                                        colWidths=[5.2 * cm, 5.2 * cm, 5.2 * cm],
                                    )
                                    t_imgs.setStyle(TableStyle([
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.HexColor('#e5e7eb')),
                                    ]))
                                    elementos.append(t_imgs)
                                    elementos.append(Spacer(1, 4))
                                    linha_imgs = []
                            else:
                                elementos.append(Paragraph(
                                    f'[Imagem não encontrada: {img_anexo.descricao or "sem descrição"}]',
                                    estilo_anexo_desc,
                                ))
                        except Exception:
                            elementos.append(Paragraph(
                                f'[Erro ao carregar imagem: {img_anexo.descricao or "sem descrição"}]',
                                estilo_anexo_desc,
                            ))

                # Referenciar vídeos no PDF
                if videos_anexo:
                    elementos.append(Paragraph(
                        f'Vídeos anexados ({len(videos_anexo)}):',
                        estilo_anexo_titulo,
                    ))
                    for idx_vid, vid_anexo in enumerate(videos_anexo, 1):
                        nome_arquivo = os.path.basename(str(vid_anexo.video)) if vid_anexo.video else '—'
                        desc = vid_anexo.descricao or 'Sem descrição'
                        upload_dt = vid_anexo.data_upload.strftime('%d/%m/%Y %H:%M') if vid_anexo.data_upload else '—'
                        elementos.append(Paragraph(
                            f'🎬 Vídeo {idx_vid}: <b>{nome_arquivo}</b> — {desc} '
                            f'(upload: {upload_dt}) — '
                            f'<i>Disponível para consulta no sistema PIEVDCS.</i>',
                            estilo_video_ref,
                        ))

                elementos.append(Spacer(1, 4))

            elementos.append(HRFlowable(
                width='100%', thickness=0.3,
                color=colors.HexColor('#eeeeee'),
                spaceBefore=4, spaceAfter=8,
            ))

    else:
        elementos.append(Paragraph(
            'Nenhum atendimento registrado para esta medida protetiva.',
            estilo_corpo_sem_recuo,
        ))

    elementos.append(Spacer(1, 12))

    # === Fechamento ===
    elementos.append(Paragraph(
        'Sem mais para o momento, colocamo-nos à disposição para '
        'eventuais esclarecimentos que se façam necessários.',
        estilo_corpo,
    ))
    elementos.append(Paragraph('Atenciosamente,', estilo_corpo_sem_recuo))
    elementos.append(Spacer(1, 40))

    # === Assinatura ===
    profissional = request.user.get_full_name() or request.user.username
    elementos.append(HRFlowable(
        width='50%', thickness=0.5, color=colors.black,
    ))
    elementos.append(Paragraph(profissional, estilo_assinatura))
    elementos.append(Paragraph(
        'Instituição: Polícia Militar — Rede Catarina', estilo_cargo,
    ))
    elementos.append(Spacer(1, 20))

    # === Rodapé ===
    elementos.append(HRFlowable(
        width='100%', thickness=0.5,
        color=colors.HexColor('#ddd'), spaceAfter=4,
    ))
    elementos.append(Paragraph(
        f'Documento gerado em {agora.strftime("%d/%m/%Y %H:%M")} '
        f'por {profissional}',
        estilo_rodape,
    ))
    elementos.append(Paragraph(
        'PIEVDCS — Plataforma Integrada de Enfrentamento à '
        'Violência Doméstica e Crimes Sexuais',
        estilo_rodape,
    ))

    doc.build(elementos)
    buf.seek(0)

    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="oficio_rede_catarina_mp_{medida.ID}.pdf"'
    )
    return response