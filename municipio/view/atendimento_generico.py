# municipio/view/atendimento_generico.py
"""
Funções genéricas de atendimento para instituições municipais.
CREAS, CRAS, CAPS e Secretaria da Saúde delegam para estas funções.
"""
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Func, F, Value, CharField
from django.utils import timezone
from datetime import timedelta

from mensageria.models import Notificacao
from seguranca_publica.models.penal import tipo_atendimento, ModeloPenal
from sistema_justica.models.base import Agressor_dados
from municipio.forms.municipio_forms import MunicipioAtendimentoForm

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
import io


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

MESES_PT = {
    'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
    'April': 'abril', 'May': 'maio', 'June': 'junho', 'July': 'julho',
    'August': 'agosto', 'September': 'setembro', 'October': 'outubro',
    'November': 'novembro', 'December': 'dezembro',
}


def _ctx(config, extra=None):
    """Monta contexto base com URL names para os templates."""
    ctx = {
        'instituicao': config['instituicao'],
        'url_cadastro_form': config['url_names']['cadastro_form'],
        'url_cadastro_submit': config['url_names']['cadastro_submit'],
        'url_mostra_todos': config['url_names']['mostra_todos'],
        'url_edita': config['url_names']['edita'],
        'url_buscar_cpf': config['url_names']['buscar_cpf'],
        'url_relatorio_cpf_popup': config['url_names']['relatorio_cpf_popup'],
        'url_gerar_relatorio_cpf': config['url_names']['gerar_relatorio_cpf'],
        'url_relatorio_atendimento': config['url_names']['relatorio_atendimento'],
    }
    if extra:
        ctx.update(extra)
    return ctx


def _data_extenso(dt):
    """Data formatada em português."""
    s = dt.strftime('%d de %B de %Y')
    for eng, pt in MESES_PT.items():
        s = s.replace(eng, pt)
    return s


def _estilos_pdf(cor_hex):
    """Estilos ReportLab parametrizados pela cor da instituição."""
    styles = getSampleStyleSheet()
    cor = colors.HexColor(cor_hex)
    base = styles['Normal']
    return {
        'cor': cor,
        'cab': ParagraphStyle('Cab', parent=base, fontName='Helvetica-Bold',
                              fontSize=12, alignment=TA_CENTER, spaceAfter=2, textColor=cor),
        'sub': ParagraphStyle('Sub', parent=base, fontName='Helvetica',
                              fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#4a4a4a')),
        'subtit': ParagraphStyle('SubT', parent=base, fontName='Helvetica',
                                 fontSize=8, alignment=TA_CENTER, textColor=colors.gray, spaceAfter=6),
        'corpo': ParagraphStyle('Corpo', parent=base, fontSize=11,
                                alignment=TA_JUSTIFY, firstLineIndent=2*cm, spaceAfter=10, leading=16),
        'corpo_sr': ParagraphStyle('CorpoSR', parent=base, fontSize=11,
                                   alignment=TA_JUSTIFY, spaceAfter=10, leading=16),
        'secao': ParagraphStyle('Secao', parent=base, fontName='Helvetica-Bold',
                                fontSize=9, textColor=cor, spaceAfter=6, spaceBefore=12),
        'assunto': ParagraphStyle('Assunto', parent=base, fontName='Helvetica-Bold',
                                  fontSize=10, alignment=TA_CENTER, spaceAfter=4, textColor=cor),
        'assin': ParagraphStyle('Assin', parent=base, fontName='Helvetica-Bold',
                                fontSize=10, alignment=TA_CENTER),
        'cargo': ParagraphStyle('Cargo', parent=base, fontName='Helvetica',
                                fontSize=8, alignment=TA_CENTER, textColor=colors.gray),
        'rodape': ParagraphStyle('Rodape', parent=base, fontName='Helvetica',
                                 fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor('#999')),
        'esq': ParagraphStyle('Esq', parent=base, fontName='Helvetica-Bold',
                              fontSize=11, textColor=cor),
        'dir': ParagraphStyle('Dir', parent=base, fontSize=10, alignment=TA_RIGHT),
    }


def _cabecalho_pdf(elementos, est, instituicao, subtitulo):
    """Adiciona cabeçalho padrão ao PDF."""
    elementos.append(Paragraph(
        'PLATAFORMA INTEGRADA DE ENFRENTAMENTO À VIOLÊNCIA<br/>'
        'DOMÉSTICA E CRIMES SEXUAIS', est['cab']))
    elementos.append(Paragraph(f'{instituicao} — {subtitulo}', est['sub']))
    elementos.append(Paragraph('PIEVDCS — Sistema de Gestão Integrada', est['subtit']))
    elementos.append(HRFlowable(width='100%', thickness=2, color=est['cor'], spaceAfter=20))


def _identificacao_pdf(elementos, est, rotulo, numero, agora):
    """Linha de identificação (número + data) no PDF."""
    data_str = _data_extenso(agora)
    tb = Table([[
        Paragraph(f'{rotulo} Nº {numero}/{agora.strftime("%Y")}', est['esq']),
        Paragraph(data_str, est['dir']),
    ]], colWidths=[8*cm, 7.7*cm])
    tb.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementos.append(tb)
    elementos.append(Spacer(1, 12))


def _rodape_pdf(elementos, est, instituicao, agora, usuario):
    """Assinatura e rodapé do PDF."""
    elementos.append(Paragraph(
        'Sem mais, colocamo-nos à disposição.', est['corpo']))
    elementos.append(Paragraph('Atenciosamente,', est['corpo_sr']))
    elementos.append(Spacer(1, 40))
    elementos.append(HRFlowable(width='50%', thickness=0.5, color=colors.black))
    elementos.append(Paragraph(usuario, est['assin']))
    elementos.append(Paragraph(f'{instituicao} — PIEVDCS', est['cargo']))
    elementos.append(Spacer(1, 20))
    elementos.append(HRFlowable(
        width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=4))
    elementos.append(Paragraph(
        f'Documento gerado em {agora.strftime("%d/%m/%Y %H:%M")} por {usuario}',
        est['rodape']))
    elementos.append(Paragraph(
        'PIEVDCS — Plataforma Integrada de Enfrentamento à Violência '
        'Doméstica e Crimes Sexuais', est['rodape']))


def _tabela_estilizada(dados, col_widths, cor):
    """Cria tabela com estilo padrão."""
    tb = Table(dados, colWidths=col_widths)
    tb.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), cor),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#f9f9f9')]),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ]))
    return tb


def _buscar_agressor(busca):
    """Busca agressor por CPF ou nome."""
    busca_limpa = busca.replace('.', '').replace('-', '').replace(' ', '')
    agressor = None
    if busca_limpa.isdigit() and len(busca_limpa) == 11:
        agressor = Agressor_dados.objects.annotate(
            cpf_limpo=Func(
                Func(F('cpf'), Value('.'), Value(''), function='replace'),
                Value('-'), Value(''),
                function='replace', output_field=CharField()
            )
        ).filter(cpf_limpo=busca_limpa).first()
    if not agressor:
        agressor = Agressor_dados.objects.filter(nome__icontains=busca).first()
    return agressor


# ──────────────────────────────────────────────
# Views genéricas
# ──────────────────────────────────────────────

def dashboard_instituicao(request, config):
    """Dashboard principal de uma instituição."""
    inst = config['instituicao']
    try:
        notif = Notificacao.contar_nao_lidas_usuario(request.user)
    except Exception:
        notif = 0

    now = timezone.now()
    inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    inicio_mes_ant = (inicio_mes - timedelta(days=1)).replace(day=1)
    fim_mes_ant = inicio_mes - timedelta(seconds=1)

    base_qs = ModeloPenal.objects.filter(
        atendimento__instituicao_responsavel=inst
    )
    try:
        qtd_mes = base_qs.filter(
            usuario=request.user,
            data_atendimento__gte=inicio_mes,
            data_atendimento__lte=now,
        ).count()
        qtd_ant = base_qs.filter(
            data_atendimento__gte=inicio_mes_ant,
            data_atendimento__lte=fim_mes_ant,
        ).count()
        variacao = (
            ((qtd_mes - qtd_ant) / qtd_ant) * 100 if qtd_ant > 0
            else (100 if qtd_mes > 0 else 0)
        )
        atendimentos = base_qs.filter(
            usuario=request.user
        ).select_related('atendimento').prefetch_related(
            'agressores_atendidos'
        ).order_by('-id')

        grupos = [{
            'id': a.id,
            'nome': f'Atendimento {a.id} - {a.data_atendimento:%d/%m/%Y %H:%M}',
            'qtd_agressores': a.agressores_atendidos.count(),
            'participantes': a.agressores_atendidos.all(),
        } for a in atendimentos]
    except Exception:
        qtd_mes = variacao = 0
        grupos = []

    tipo_count = tipo_atendimento.objects.filter(
        instituicao_responsavel=inst
    ).count()

    return render(request, config['template_principal'], _ctx(config, {
        'title': config['titulo'],
        'encaminhamentos': 2,
        'notificacao': notif,
        'qtd_atendimentos': qtd_mes,
        'variacao_atendimentos': variacao,
        'tipo_atendimentos': tipo_count,
        'grupos': grupos,
        'user': request.user,
    }))


def cadastro_form(request, config):
    """Formulário de cadastro de atendimento."""
    form = MunicipioAtendimentoForm(instituicao=config['instituicao'])
    return render(request, 'parcial/cadastro_atendimento_form.html', _ctx(config, {
        'form': form,
    }))


def cadastro_submit(request, config):
    """Salva atendimento."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    form = MunicipioAtendimentoForm(
        request.POST, instituicao=config['instituicao']
    )
    if form.is_valid():
        obj = form.save(commit=False)
        obj.usuario = request.user
        obj.save()
        form.save_m2m()
        return HttpResponse(
            '<script>'
            'exibirPopupSucesso("Atendimento cadastrado com sucesso!", "sucesso");'
            'setTimeout(() => { document.querySelector(".fixed.inset-0").remove(); }, 500);'
            '</script>'
        )
    return render(request, 'parcial/cadastro_atendimento_form.html', _ctx(config, {
        'form': form,
    }))


def mostra_todos(request, config):
    """Lista todos os atendimentos da instituição."""
    inst = config['instituicao']
    grupos = ModeloPenal.objects.filter(
        atendimento__instituicao_responsavel=inst
    ).select_related(
        'usuario', 'atendimento'
    ).prefetch_related('agressores_atendidos').order_by('-data_atendimento')

    now = timezone.now()
    return render(request, 'parcial/mostra_todos_atendimentos.html', _ctx(config, {
        'title': f'Todos os Atendimentos — {inst}',
        'grupos': grupos,
        'qtd_de_grupos': grupos.count(),
        'qtd_de_grupos_mes': grupos.filter(
            data_atendimento__month=now.month,
            data_atendimento__year=now.year,
        ).count(),
        'agressores_totais': sum(
            g.agressores_atendidos.count() for g in grupos
        ),
        'agressores_unicos_totais': Agressor_dados.objects.filter(
            agressores_atendidos__in=grupos
        ).distinct().count(),
        'user': request.user,
    }))


def edita_atendimento(request, grupo_id, config):
    """Edita um atendimento."""
    try:
        grupo = ModeloPenal.objects.prefetch_related(
            'agressores_atendidos', 'usuario'
        ).get(id=grupo_id)
    except ModeloPenal.DoesNotExist:
        return HttpResponse(
            '<div class="p-4 bg-red-50 border-l-4 border-red-500 '
            'rounded-lg text-center"><p class="text-sm text-red-700">'
            'Atendimento não encontrado.</p></div>', status=404
        )

    inst = config['instituicao']
    if request.method == 'POST':
        form = MunicipioAtendimentoForm(
            request.POST, instance=grupo, instituicao=inst
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.atualizado_por = request.user
            obj.save()
            form.save_m2m()
            url = reverse(config['url_names']['mostra_todos'])
            return HttpResponse(
                '<script>'
                'exibirPopupSucesso("✅ Atendimento atualizado!", "sucesso");'
                'document.getElementById("modal-container").innerHTML = "";'
                f'htmx.ajax("GET", "{url}", '
                '{target: "#lista-grupos", swap: "innerHTML"});'
                '</script>'
            )
    else:
        form = MunicipioAtendimentoForm(instance=grupo, instituicao=inst)

    return render(request, 'parcial/edita_atendimento.html', _ctx(config, {
        'form': form, 'grupo': grupo, 'user': request.user,
    }))


def buscar_cpf_modal(request, config):
    """Modal de busca por CPF."""
    inst = config['instituicao']
    resultado = ""

    if request.method == "POST":
        cpf = request.POST.get('cpf', '').replace('.', '').replace('-', '').strip()
        if not cpf:
            resultado = '<span class="text-red-600">CPF não informado.</span>'
        else:
            try:
                agressor = Agressor_dados.objects.annotate(
                    cpf_limpo=Func(
                        Func(F('cpf'), Value('.'), Value(''), function='replace'),
                        Value('-'), Value(''),
                        function='replace', output_field=CharField()
                    )
                ).get(cpf_limpo=cpf)

                atends = agressor.agressores_atendidos.filter(
                    atendimento__instituicao_responsavel=inst
                ).order_by('-data_atendimento')
                qtd = atends.count()

                if qtd > 0:
                    ultimo = atends.first().data_atendimento.strftime("%d/%m/%Y %H:%M")
                    resultado = (
                        f'<div class="bg-green-50 border border-green-200 rounded-lg p-4">'
                        f'<span class="text-green-700 font-semibold">'
                        f'Nome: {agressor.nome}<br>CPF: {agressor.cpf}<br>'
                        f'Total de atendimentos ({inst}): {qtd}</span>'
                        f'<div class="mt-2 text-sm text-green-600">'
                        f'Último: {ultimo}</div></div>'
                    )
                else:
                    resultado = (
                        f'<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">'
                        f'<span class="text-yellow-700">{agressor.nome} — '
                        f'CPF: {agressor.cpf}<br>'
                        f'Nenhum atendimento no {inst}.</span></div>'
                    )
            except Agressor_dados.DoesNotExist:
                resultado = '<span class="text-red-600">CPF não encontrado.</span>'

    html = render_to_string('parcial/modal_busca_cpf.html', _ctx(config, {
        'resultado': resultado,
    }), request)
    return HttpResponse(html)


def relatorio_cpf_popup(request, config):
    """Popup de busca para relatório PDF."""
    return render(request, 'parcial/relatorio_por_cpf_popup.html', _ctx(config))


def gerar_relatorio_por_cpf(request, config):
    """Gera relatório PDF por CPF/nome filtrado pela instituição."""
    inst = config['instituicao']
    cor_hex = config['cor_hex']
    busca = request.GET.get('busca', '').strip()

    if not busca:
        return HttpResponse('Nenhum termo informado.', status=400)

    agressor = _buscar_agressor(busca)
    if not agressor:
        return HttpResponse(
            f'Nenhum registro encontrado para: "{busca}"', status=404
        )

    atendimentos = ModeloPenal.objects.filter(
        agressores_atendidos=agressor,
        atendimento__instituicao_responsavel=inst,
    ).select_related(
        'usuario', 'atendimento', 'atualizado_por'
    ).order_by('-data_atendimento')

    # === PDF ===
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=3*cm, rightMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm
    )
    agora = timezone.localtime(timezone.now())
    est = _estilos_pdf(cor_hex)
    el = []

    _cabecalho_pdf(el, est, inst, 'Relatório Individual de Atendimentos')
    _identificacao_pdf(el, est, 'RELATÓRIO', agressor.id, agora)

    # Assunto
    el.append(HRFlowable(
        width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=4))
    el.append(Paragraph(
        f'ASSUNTO: Relatório de Atendimentos — {agressor.nome}', est['assunto']))
    el.append(HRFlowable(
        width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=16))

    # Dados do acompanhado
    el.append(Paragraph('DADOS DO ACOMPANHADO', est['secao']))
    dados = [['Nome Completo:', agressor.nome], ['CPF:', agressor.cpf]]
    if hasattr(agressor, 'data_nascimento') and agressor.data_nascimento:
        dados.append([
            'Data de Nascimento:', agressor.data_nascimento.strftime('%d/%m/%Y')
        ])
    tb = Table(dados, colWidths=[5*cm, 10.7*cm])
    tb.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#eee')),
    ]))
    el.append(tb)
    el.append(Spacer(1, 16))

    # Corpo
    qtd = atendimentos.count()
    el.append(Paragraph(
        f'Informamos que o(a) acompanhado(a) <b>{agressor.nome}</b>, '
        f'CPF <b>{agressor.cpf}</b>, possui <b>{qtd}</b> atendimento(s) '
        f'registrado(s) no <b>{inst}</b>.', est['corpo']))
    el.append(Spacer(1, 8))

    # Tabela de atendimentos
    estilo_celula = ParagraphStyle(
    'celula_tabela', fontName='Helvetica', fontSize=8, leading=10
    )
    el.append(Paragraph('HISTÓRICO DE ATENDIMENTOS', est['secao']))
    linhas = [['id', 'Data', 'Setor', 'Tipo', 'Duração', 'Profissional']]
    for i, at in enumerate(atendimentos, 1):
        linhas.append([
            str(i),
            at.data_atendimento.strftime('%d/%m/%Y %H:%M'),
            Paragraph(at.setor_atendimento or '—', estilo_celula),
            Paragraph(str(at.atendimento) if at.atendimento else '—', estilo_celula),
            str(at.tempo_atendimento) if at.tempo_atendimento else '—',
            Paragraph(at.usuario.get_full_name() if at.usuario else '—', estilo_celula),
        ])
    if qtd == 0:
        linhas.append(['', '', 'Nenhum atendimento registrado', '', '', ''])
    el.append(_tabela_estilizada(
        linhas, [0.8*cm, 3*cm, 3*cm, 3.5*cm, 2.2*cm, 3.2*cm], est['cor']
    ))
    el.append(Spacer(1, 12))

    # Avaliações
    com_av = atendimentos.exclude(avaliacao__isnull=True).exclude(avaliacao='')
    if com_av.exists():
        el.append(Paragraph('AVALIAÇÕES DOS ATENDIMENTOS', est['secao']))
        for at in com_av:
            el.append(Paragraph(
                f'<b>Atendimento nº {at.id} — '
                f'{at.data_atendimento.strftime("%d/%m/%Y")}:</b>',
                est['corpo_sr']))
            el.append(Paragraph(
                at.avaliacao.replace('\n', '<br/>'), est['corpo_sr']))

    usuario_gerou = request.user.get_full_name() or request.user.username
    _rodape_pdf(el, est, inst, agora, usuario_gerou)

    doc.build(el)
    buffer.seek(0)
    cpf_arq = agressor.cpf.replace('.', '').replace('-', '')
    resp = HttpResponse(buffer, content_type='application/pdf')
    resp['Content-Disposition'] = (
        f'inline; filename="relatorio_{config["pdf_prefix"]}_{cpf_arq}.pdf"'
    )
    return resp


def gerar_relatorio_atendimento(request, grupo_id, config):
    """Gera PDF de um atendimento individual."""
    inst = config['instituicao']
    cor_hex = config['cor_hex']

    try:
        grupo = ModeloPenal.objects.select_related(
            'usuario', 'atendimento', 'atualizado_por'
        ).prefetch_related('agressores_atendidos').get(id=grupo_id)
    except ModeloPenal.DoesNotExist:
        return HttpResponse('Atendimento não encontrado.', status=404)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=3*cm, rightMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm
    )
    agora = timezone.localtime(timezone.now())
    est = _estilos_pdf(cor_hex)
    el = []

    _cabecalho_pdf(el, est, inst, 'Atendimento')
    _identificacao_pdf(el, est, 'OFÍCIO', grupo.id, agora)

    # Assunto
    el.append(HRFlowable(
        width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=4))
    el.append(Paragraph(
        f'ASSUNTO: Relatório de Atendimento — Registro nº {grupo.id}',
        est['assunto']))
    el.append(HRFlowable(
        width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=16))

    # Corpo
    data_at = grupo.data_atendimento.strftime('%d/%m/%Y')
    hora_at = grupo.data_atendimento.strftime('%H:%M')
    tipo_txt = (
        f', com a temática <b>{grupo.atendimento}</b>'
        if grupo.atendimento else ''
    )
    dur_txt = (
        f', com duração de <b>{grupo.tempo_atendimento}</b>'
        if grupo.tempo_atendimento else ''
    )
    el.append(Paragraph(
        f'Comunicamos que no dia <b>{data_at}</b>, às <b>{hora_at}</b>, '
        f'foi realizado atendimento no setor de '
        f'<b>{grupo.setor_atendimento}</b>{tipo_txt}{dur_txt}.', est['corpo']))

    # Participantes
    participantes = grupo.agressores_atendidos.all()
    qtd = participantes.count()
    el.append(Paragraph(
        f'O atendimento contou com <b>{qtd}</b> participante(s):', est['corpo']))
    el.append(Spacer(1, 8))

    linhas = [['#', 'Nome Completo', 'CPF']]
    for i, ag in enumerate(participantes, 1):
        linhas.append([str(i), ag.nome, ag.cpf])
    if qtd == 0:
        linhas.append(['', 'Nenhum participante registrado', ''])
    el.append(_tabela_estilizada(
        linhas, [1.2*cm, 10*cm, 4.5*cm], est['cor']
    ))
    el.append(Spacer(1, 12))

    # Avaliação
    if grupo.avaliacao:
        el.append(Paragraph('AVALIAÇÃO DO ATENDIMENTO', est['secao']))
        el.append(Paragraph(
            grupo.avaliacao.replace('\n', '<br/>'), est['corpo_sr']))

    # Informações complementares
    el.append(Paragraph('INFORMAÇÕES COMPLEMENTARES', est['secao']))
    prof = (
        grupo.usuario.get_full_name() or grupo.usuario.username
        if grupo.usuario else '—'
    )
    criado = (
        grupo.criado_em.strftime('%d/%m/%Y %H:%M') if grupo.criado_em else '—'
    )
    info = [['Profissional:', prof], ['Data de Registro:', criado]]
    if grupo.atualizado_por:
        nome_at = (
            grupo.atualizado_por.get_full_name()
            or grupo.atualizado_por.username
        )
        data_at_str = (
            grupo.atualizado_em.strftime('%d/%m/%Y %H:%M')
            if grupo.atualizado_em else ''
        )
        info.append(['Última Atualização:', f'{data_at_str} por {nome_at}'])

    tb_info = Table(info, colWidths=[5.5*cm, 10.2*cm])
    tb_info.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#eee')),
    ]))
    el.append(tb_info)
    el.append(Spacer(1, 20))

    usuario_gerou = request.user.get_full_name() or request.user.username
    _rodape_pdf(el, est, inst, agora, usuario_gerou)

    doc.build(el)
    buffer.seek(0)
    resp = HttpResponse(buffer, content_type='application/pdf')
    resp['Content-Disposition'] = (
        f'inline; filename="oficio_{config["pdf_prefix"]}_{grupo_id}.pdf"'
    )
    return resp