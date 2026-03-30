# -*- coding: utf-8 -*-
#import openai #Precisa PAGAR
from django.shortcuts import render, redirect, get_object_or_404
import requests
import traceback
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from .permission_group import grupos_permitidos
from django.core.paginator import Paginator
from django.db.models import Case, When, IntegerField as IntField
from ..forms.cadastros import CadastroVitimaForm, CadastroAgressorForm, CadastroMunicipioForm
from ..models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado
from ..models.defensoria_publica import FormularioMedidaProtetiva
from ..models.poder_judiciario import ComarcasPoderJudiciario
from MAIN.utils.email_utils import enviar_email_grupo
from seguranca_publica.models.militar import AtendimentosRedeCatarina
from seguranca_publica.models.penal import ModeloPenal
from django.template.loader import render_to_string
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from datetime import date, datetime, timedelta
from django.db.models import Q, F, Value, BooleanField, IntegerField, ExpressionWrapper, Count
from django.db.models.functions import Cast
from django.contrib.auth.models import Group
from urllib.parse import urlencode
from django.utils import timezone

from MAIN.decoradores.calcula_tempo import calcula_tempo

ANO_CORRENTE = date.today().year

""" Configuraçao de decoradores para debug """
import os

var_debug = os.getenv('DEBUG')

if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
    
else:
    checked_debug_decorador = lambda x: x
    checked_debug_decorador_fun = lambda x: x

""" Fim da configuraçao de decoradores para debug """







@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário',])
def poder_judiciario(request):
    """Renderiza o dashboard do Poder Judiciário com métricas reais do banco."""
    
    hoje = date.today()
    notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)
    encaminhamentos_nao_lidos = Notificacao.contar_encaminhamentos_nao_lidos(request.user)

    # Total de MPs (casos)
    total_mp = FormularioMedidaProtetiva.objects.count()

    # MPs ativas (período não expirado)
    mp_ativas = FormularioMedidaProtetiva.objects.filter(periodo_mp__gte=hoje).count()

    # MPs vencidas
    mp_vencidas = total_mp - mp_ativas

    # Alto risco: MPU + indicadores graves (exibia armas, ameaça matar, ideação suicida)
    mp_alto_risco = FormularioMedidaProtetiva.objects.filter(
        periodo_mp__gte=hoje,
        solicitada_mpu=True,
    ).filter(
        Q(exibia_armas=True) |
        Q(ameaca_se_matar=True) |
        Q(perdeu_vontade_viver_suicida=True) |
        Q(filhos_riscos=True)
    ).count()

    # Atendimentos hoje (solicitações feitas na data atual)
    atendimentos_hoje = FormularioMedidaProtetiva.objects.filter(
        data_solicitacao__date=hoje
    ).count()

    # MPs a vencer nos próximos 15 dias
    mp_vencer_15dias = FormularioMedidaProtetiva.objects.filter(
        periodo_mp__gte=hoje,
        periodo_mp__lte=hoje + timedelta(days=15)
    ).count()

    # Último atendimento do dia
    ultimo_atendimento = FormularioMedidaProtetiva.objects.filter(
        data_solicitacao__date=hoje
    ).order_by('-data_solicitacao').values_list('data_solicitacao', flat=True).first()

    descumprimento_mpu = AtendimentosRedeCatarina.objects.filter(vitima_relatou_descumprimento=True
        ).count()

    contexto = {
        'title': 'Poder Judiciário',
        'description': 'Informações e ações pertinentes ao poder Judiciário.',
        'ano_corrente': ANO_CORRENTE,
        'encaminhamentos': encaminhamentos_nao_lidos,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'user': request.user,
        'total_mp': total_mp,
        'mp_vencer_15dias': mp_vencer_15dias,
        'mp_ativas': mp_ativas,
        'mp_vencidas': mp_vencidas,
        'mp_alto_risco': mp_alto_risco,
        'atendimentos_hoje': atendimentos_hoje,
        'ultimo_atendimento': ultimo_atendimento,
        'descumprimento_mpu': descumprimento_mpu,
    }
    return render(request, "judiciario_IA.html", contexto)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def cadastro_vitima_form(request):
    form = CadastroVitimaForm()
    return render(request, 'parcial/cadastro_vitima_form.html', {'form': form})


@login_required(login_url=reverse_lazy('login'))
def cadastro_vitima_submit(request):
    if request.method == 'POST':
        form = CadastroVitimaForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(
                """
                    <script>
                        exibirPopupSucesso('Vítima cadastrada com sucesso!', 'feminino');
                        document.getElementById('modal-vitima').innerHTML = '';
                    </script>
                """
            )
    else:
        return render(request, "parcial/cadastro_vitima_form.html", {"form": form})
    return HttpResponse(status=405)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def cadastro_agressor_form(request):
    form = CadastroAgressorForm()
    return render(request, 'parcial/cadastro_agressor_form.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def cadastro_agressor_submit(request):
    if request.method == 'POST':
        form = CadastroAgressorForm(request.POST)
        if form.is_valid():
            agressor = form.save()
            # Retorne um script para fechar o modal e recarregar o campo agressor do formulário de vítima
            return HttpResponse(
                """
                    <script>
                        exibirPopupSucesso('Agressor cadastrado com sucesso!', 'masculino');
                        document.getElementById('modal-agressor').innerHTML = '';
                        htmx.trigger(htmx.find('#id_agressor'), 'change');
                    </script>
                """
            )
        else:
            return render(request, 'parcial/cadastro_agressor_form.html', {'form': form})
    return HttpResponse(status=405)

@login_required(login_url=reverse_lazy('login'))
def cadastro_municipio_form(request):
    form = CadastroMunicipioForm()
    return render(request, 'parcial/cadastro_municipio_form.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def cadastro_municipio_submit(request):
    if request.method == 'POST':
        form = CadastroMunicipioForm(request.POST)
        if form.is_valid():
            municipio = form.save()
            return HttpResponse("""
                <script>
                    document.getElementById('modal-municipio').innerHTML = '';
                    // Opcional: recarregar o campo municipio via HTMX
                    htmx.trigger(htmx.find('#id_municipio'), 'change');
                </script>
                <div class="alert alert-success">Município cadastrado com sucesso! Selecione-o na lista.</div>
            """)
        else:
            return render(request, 'parcial/cadastro_municipio_form.html', {'form': form})
    return HttpResponse(status=405)



@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário', 'Defensoria Pública', 'Ministério Público'])
def listar_medidas_protetivas(request):
    """Lista medidas protetivas com paginação de 50 registros e scroll infinito."""
    

    filtro_status  = request.GET.get('status', 'todas')
    filtro_ordenar = request.GET.get('ordenar', 'periodo_mp')
    filtro_busca   = request.GET.get('busca', '').strip()
    filtro_comarca = request.GET.get('comarca', '')
    pagina         = max(int(request.GET.get('pagina', 1)), 1)

    hoje = date.today()

    qs = FormularioMedidaProtetiva.objects.select_related(
        'vitima', 'agressor', 'comarca_competente'
    )

    # Filtros aplicados no banco
    if filtro_status == 'ativas':
        qs = qs.filter(periodo_mp__gte=hoje)
    elif filtro_status == 'vencidas':
        qs = qs.filter(periodo_mp__lt=hoje)

    if filtro_comarca:
        qs = qs.filter(comarca_competente_id=filtro_comarca)

    if filtro_busca:
        qs = qs.filter(
            Q(vitima__nome__icontains=filtro_busca) |
            Q(vitima__cpf__icontains=filtro_busca) |
            Q(agressor__nome__icontains=filtro_busca) |
            Q(agressor__cpf__icontains=filtro_busca)
        )

    # Ordenação no banco: ativas primeiro, depois pelo campo escolhido
    ordenacoes_permitidas = ['periodo_mp', '-periodo_mp', '-data_solicitacao']
    if filtro_ordenar not in ordenacoes_permitidas:
        filtro_ordenar = 'periodo_mp'

    qs = qs.annotate(
        _ativa=Case(
            When(periodo_mp__gte=hoje, then=0),
            default=1,
            output_field=IntField(),
        )
    ).order_by('_ativa', filtro_ordenar)

    # Paginação
    paginator  = Paginator(qs, 50)
    pagina_obj = paginator.get_page(pagina)

    # Calcula propriedades apenas nos 50 registros da página
    for mp in pagina_obj:
        mp.ativa = mp.periodo_mp >= hoje
        mp.dias_restantes = (mp.periodo_mp - hoje).days if mp.ativa else 0

    # Query string dos filtros para o sentinela de scroll
    filtros_qs = urlencode({k: v for k, v in {
        'status':  filtro_status,
        'ordenar': filtro_ordenar,
        'busca':   filtro_busca,
        'comarca': filtro_comarca,
    }.items() if v and v != 'todas'})

    comarcas = ComarcasPoderJudiciario.objects.only('id', 'nome').order_by('nome')

    contexto = {
        'medidas':           pagina_obj,
        'pagina_obj':        pagina_obj,
        'tem_proxima':       pagina_obj.has_next(),
        'proxima_pagina':    pagina_obj.next_page_number() if pagina_obj.has_next() else None,
        'total':             paginator.count,
        'filtros_qs':        filtros_qs,
        'filtro_status':     filtro_status,
        'filtro_ordenar':    filtro_ordenar,
        'filtro_busca':      filtro_busca,
        'filtro_comarca':    filtro_comarca,
        'comarcas':          comarcas,
        'pode_alterar_periodo': request.user.groups.filter(name='Poder Judiciário').exists(),
    }

    # Scroll infinito → retorna apenas as novas linhas + novo sentinela
    if request.headers.get('HX-Target') == 'sentinela-mp':
        return render(request, 'parcial/judiciario/linhas_medidas_protetivas.html', contexto)

    # Filtro HTMX → retorna tabela completa (reinicia página 1)
    if request.headers.get('HX-Target') == 'tabela-medidas':
        return render(request, 'parcial/judiciario/tabela_medidas_protetivas.html', contexto)

    return render(request, 'parcial/judiciario/listar_medidas_protetivas.html', contexto)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário'])
def form_alterar_periodo_mp(request, medida_id):
    """Retorna o formulário popup para alterar o período da MP."""

    hoje = date.today()
    medida = FormularioMedidaProtetiva.objects.select_related('vitima').get(ID=medida_id)
    medida.ativa = medida.periodo_mp >= hoje
    medida.dias_restantes = (medida.periodo_mp - hoje).days if medida.ativa else 0

    return render(request, 'parcial/judiciario/form_alterar_periodo_mp.html', {
        'medida': medida,
    })

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário'])
def alterar_periodo_mp(request, medida_id):
    """Processa a alteração do período da medida protetiva."""

    if request.method != 'POST':
        return HttpResponse(status=405)

    medida = FormularioMedidaProtetiva.objects.get(ID=medida_id)
    novo_periodo_str = request.POST.get('novo_periodo', '')

    try:
        novo_periodo = datetime.strptime(novo_periodo_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return HttpResponse(
            """<script>exibirPopupSucesso('Data inválida. Tente novamente.', 'erro');</script>"""
        )

    medida.periodo_mp = novo_periodo
    medida.save(update_fields=['periodo_mp'])

    return HttpResponse(
        """<script>
            exibirPopupSucesso('Período da medida protetiva atualizado com sucesso!', 'sucesso');
            document.getElementById('modal-alterar-periodo-popup').remove();
            htmx.ajax('GET', '""" + str(reverse_lazy('sistema_justica:listar_medidas_protetivas')) + """?status=todas', {target:'#tabela-medidas', swap:'innerHTML'});
        </script>"""
    )


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário', 'Defensoria Pública', 'Ministério Público'])
@checked_debug_decorador
def detalhe_medida_protetiva_jud(request, medida_id):
    """Retorna popup com detalhes da medida protetiva para o Judiciário."""
    

    hoje = date.today()
    medida = FormularioMedidaProtetiva.objects.select_related(
        'vitima', 'agressor',
        'vitima__estado', 'vitima__municipio',
        'agressor__estado', 'agressor__municipio',
        'comarca_competente', 'municipio_mp',
    ).prefetch_related(
        'tipo_de_violencia', 'filhos',
    ).get(ID=medida_id)

    medida.ativa = medida.periodo_mp >= hoje
    medida.dias_restantes = (medida.periodo_mp - hoje).days if medida.ativa else 0

    return render(request, 'parcial/judiciario/detalhe_medida_protetiva_jud.html', {
        'medida': medida,
    })



@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário', 'Defensoria Pública', 'Ministério Público'])
def listar_grupos_reflexivos(request):
    """
    Lista atendimentos de grupos reflexivos da Polícia Penal
    para visualização pelo Poder Judiciário (somente leitura).
    dir: sistema_justica/views/poder_judiciario.py
    """
    

    # Filtros
    filtro_setor = request.GET.get('setor', '')
    filtro_ordenar = request.GET.get('ordenar', '-data_atendimento')
    filtro_busca = request.GET.get('busca', '').strip()

    # Consulta otimizada
    grupos = ModeloPenal.objects.select_related(
        'usuario', 'atendimento'
    ).prefetch_related(
        'agressores_atendidos'
    )

    # Aplicar filtros
    if filtro_setor:
        grupos = grupos.filter(setor_atendimento=filtro_setor)

    if filtro_busca:
        grupos = grupos.filter(
            Q(agressores_atendidos__nome__icontains=filtro_busca) |
            Q(agressores_atendidos__cpf__icontains=filtro_busca)
        ).distinct()

    # Ordenação
    if filtro_ordenar in ('data_atendimento', '-data_atendimento'):
        grupos = grupos.order_by(filtro_ordenar)
    else:
        grupos = grupos.order_by('-data_atendimento')

    # Estatísticas
    hoje = timezone.now()
    total_grupos = grupos.count()
    total_grupos_mes = grupos.filter(
        data_atendimento__month=hoje.month,
        data_atendimento__year=hoje.year
    ).count()
    total_agressores = sum(g.agressores_atendidos.count() for g in grupos)

    
    total_agressores_unicos = Agressor_dados.objects.filter(
        agressores_atendidos__in=grupos
    ).distinct().count()

    contexto = {
        'grupos': grupos,
        'total_grupos': total_grupos,
        'total_grupos_mes': total_grupos_mes,
        'total_agressores': total_agressores,
        'total_agressores_unicos': total_agressores_unicos,
        'filtro_setor': filtro_setor,
        'filtro_ordenar': filtro_ordenar,
        'filtro_busca': filtro_busca,
    }

    # Se a requisição veio dos filtros internos, retorna só a tabela
    if request.headers.get('HX-Target') == 'tabela-grupos-reflexivos':
        return render(request, 'parcial/judiciario/tabela_grupos_reflexivos.html', contexto)

    return render(request, 'parcial/judiciario/listar_grupos_reflexivos.html', contexto)

def _filtrar_atendimentos_rede_catarina(request):
    """Aplica filtros de busca e ordenação para atendimentos da Rede Catarina."""
    filtro_ordenar = request.GET.get('ordenar', '-data_atendimento')
    filtro_busca = request.GET.get('busca', '').strip()

    atendimentos = AtendimentosRedeCatarina.objects.select_related(
        'medida_protetiva',
        'medida_protetiva__vitima',
        'medida_protetiva__agressor',
        'responsavel',
    )

    if filtro_busca:
        atendimentos = atendimentos.filter(
            Q(medida_protetiva__vitima__nome__icontains=filtro_busca) |
            Q(medida_protetiva__vitima__cpf__icontains=filtro_busca) |
            Q(medida_protetiva__agressor__nome__icontains=filtro_busca) |
            Q(medida_protetiva__agressor__cpf__icontains=filtro_busca)
        )

    if filtro_ordenar in ('data_atendimento', '-data_atendimento'):
        atendimentos = atendimentos.order_by(filtro_ordenar)
    else:
        filtro_ordenar = '-data_atendimento'
        atendimentos = atendimentos.order_by(filtro_ordenar)

    return atendimentos, filtro_ordenar, filtro_busca


@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário', 'Defensoria Pública', 'Ministério Público'])
def listar_atendimentos_rede_catarina(request):
    """Lista atendimentos da Rede Catarina para visualização pelo Poder Judiciário."""
    atendimentos, filtro_ordenar, filtro_busca = _filtrar_atendimentos_rede_catarina(request)

    query_string_pdf = urlencode({
        'ordenar': filtro_ordenar,
        'busca': filtro_busca,
    })

    contexto = {
        'atendimentos': atendimentos,
        'filtro_ordenar': filtro_ordenar,
        'filtro_busca': filtro_busca,
        'query_string_pdf': query_string_pdf,
    }

    if request.headers.get('HX-Target') == 'tabela-atendimentos-rede-catarina':
        return render(
            request,
            'parcial/judiciario/tabela_atendimentos_rede_catarina.html',
            contexto
        )

    return render(
        request,
        'parcial/judiciario/lista_atendimento_rede_catarina.html',
        contexto
    )

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário'])
def toggle_medida_concedida(request, medida_id):
    """Alterna o campo medida_protetiva_concedida. Exclusivo do Poder Judiciário."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    medida = get_object_or_404(FormularioMedidaProtetiva, ID=medida_id)
    medida.medida_protetiva_concedida = not medida.medida_protetiva_concedida
    medida.save(update_fields=['medida_protetiva_concedida'])

    # Notifica a Polícia Militar apenas ao CONCEDER (não ao revogar)
    if medida.medida_protetiva_concedida:
        try:
            grupo_pm = Group.objects.get(name='Polícia Militar')
            nome_vitima = medida.vitima.nome if medida.vitima else f'ID {medida_id}'
            # Notifica Polícia Militar
            enviar_notificacao_grupo(
                request=request,
                grupo_destinatario=grupo_pm,
                titulo='Medida Protetiva Concedida — Rede Catarina',
                mensagem=(
                    f'O Poder Judiciário concedeu a Medida Protetiva #{medida_id} '
                    f'para {nome_vitima}. Solicitamos acompanhamento via Rede Catarina.'
                ),
                tipo='MEDIDA_PROTETIVA',
                prioridade='ALTA',
                objeto_relacionado_tipo='FormularioMedidaProtetiva',
                objeto_relacionado_id=medida_id,
                importante=True,
            )
            # Envia e-mail
            # enviar_email_grupo(
            #     grupo_nome='Polícia Militar',
            #     assunto=f'[PIEVDCS] Medida Protetiva #{medida_id} Concedida — Rede Catarina',
            #     mensagem=(
            #         f'O Poder Judiciário concedeu a Medida Protetiva #{medida_id} '
            #         f'para {nome_vitima}.\n\n'
            #         f'Solicitamos acompanhamento via Rede Catarina.\n\n'
            #         f'Este é um e-mail automático do sistema PIEVDCS.'
            #     ),
            # )


            grupo_creas = Group.objects.get(name='CREAS')
            grupo_policia_penal = Group.objects.get(name='Polícia Penal')
            nome_agressor = medida.agressor.nome if medida.agressor else f'ID {medida_id}'

            # Notifica CREAS
            enviar_notificacao_grupo(
                request=request,
                grupo_destinatario=grupo_creas,
                titulo='Medida Protetiva Concedida — Grupo Reflexivo',
                mensagem=(
                    f'O Poder Judiciário concedeu a Medida Protetiva #{medida_id} '
                    f'para {nome_vitima}. Solicitamos acompanhamento do agressor {nome_agressor}.'
                ),
                tipo='ENCAMINHAMENTO',
                prioridade='ALTA',
                objeto_relacionado_tipo='FormularioMedidaProtetiva',
                objeto_relacionado_id=medida_id,
                importante=True,
            )

            # Notifica Polícia Penal
            enviar_notificacao_grupo(
                request=request,
                grupo_destinatario=grupo_policia_penal,
                titulo='Medida Protetiva Concedida — Grupo Reflexivo',
                mensagem=(
                    f'O Poder Judiciário concedeu a Medida Protetiva #{medida_id} '
                    f'para {nome_vitima}. Solicitamos acompanhamento do agressor {nome_agressor} '
                    f'nos grupos reflexivos.'
                ),
                tipo='ENCAMINHAMENTO',
                prioridade='ALTA',
                objeto_relacionado_tipo='FormularioMedidaProtetiva',
                objeto_relacionado_id=medida_id,
                importante=True,
            )
        except Group.DoesNotExist:
            pass

    url_toggle = reverse('sistema_justica:toggle_medida_concedida', args=[medida_id])
    icone = 'fa-check-circle' if medida.medida_protetiva_concedida else 'fa-times-circle'
    cor = 'text-green-600 hover:text-green-800' if medida.medida_protetiva_concedida else 'text-red-500 hover:text-red-700'
    label = 'Concedida' if medida.medida_protetiva_concedida else 'Não Concedida'

    return HttpResponse(f"""
        <span id="badge-concedida-{medida_id}"
              hx-post="{url_toggle}"
              hx-target="#badge-concedida-{medida_id}"
              hx-swap="outerHTML"
              title="Clique para alternar"
              class="inline-flex items-center gap-1 text-xs font-semibold cursor-pointer select-none {cor}">
            <i class="fas {icone}"></i>
            {label}
        </span>
    """)