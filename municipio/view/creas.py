# municipio/view/creas.py
"""
    Views do CREAS
    dir: municipio/view/creas.py
"""
from django.shortcuts import render, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db.models import Func, F, Value, CharField
from django.utils import timezone
from datetime import timedelta

from .permission_group import grupos_permitidos
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

# Constante da instituição
INSTITUICAO = 'CREAS'
GRUPO_PERMISSAO = 'CREAS'
COR_PRIMARIA = 'teal'  # Cor do tema para templates


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO_PERMISSAO])
def creas(request):
    """Dashboard principal do CREAS."""
    try:
        notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)
    except Exception:
        notificacoes_nao_lidas = 0

    now = timezone.now()
    primeiro_dia_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    primeiro_dia_mes_anterior = (primeiro_dia_mes - timedelta(days=1)).replace(day=1)
    ultimo_dia_mes_anterior = primeiro_dia_mes - timedelta(seconds=1)

    # Filtra apenas atendimentos do CREAS
    base_qs = ModeloPenal.objects.filter(
        atendimento__instituicao_responsavel=INSTITUICAO
    )

    try:
        atendimentos_mes = base_qs.filter(
            usuario=request.user,
            data_atendimento__gte=primeiro_dia_mes,
            data_atendimento__lte=now
        ).count()

        atendimentos_mes_anterior = base_qs.filter(
            data_atendimento__gte=primeiro_dia_mes_anterior,
            data_atendimento__lte=ultimo_dia_mes_anterior
        ).count()

        if atendimentos_mes_anterior > 0:
            variacao = ((atendimentos_mes - atendimentos_mes_anterior) / atendimentos_mes_anterior) * 100
        else:
            variacao = 100 if atendimentos_mes > 0 else 0

        atendimentos = base_qs.filter(
            usuario=request.user
        ).select_related('atendimento').prefetch_related('agressores_atendidos').order_by('-id')

        grupos = []
        for atendimento in atendimentos:
            grupos.append({
                'id': atendimento.id,
                'nome': f'Atendimento {atendimento.id} - {atendimento.data_atendimento:%d/%m/%Y %H:%M}',
                'qtd_agressores': atendimento.agressores_atendidos.count(),
                'participantes': atendimento.agressores_atendidos.all(),
            })

    except Exception:
        atendimentos_mes = 0
        atendimentos_mes_anterior = 0
        variacao = 0
        grupos = []

    tipo_atendimentos = tipo_atendimento.objects.filter(
        instituicao_responsavel=INSTITUICAO
    ).count()

    contexto = {
        'title': 'CREAS',
        'instituicao': INSTITUICAO,
        'encaminhamentos': 2,
        'notificacao': notificacoes_nao_lidas,
        'qtd_atendimentos': atendimentos_mes,
        'variacao_atendimentos': variacao,
        'tipo_atendimentos': tipo_atendimentos,
        'grupos': grupos,
        'user': request.user,
    }
    return render(request, 'creas.html', contexto)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO_PERMISSAO])
def cadastro_atendimento_creas_form(request):
    """Formulário de cadastro de atendimento CREAS."""
    form = MunicipioAtendimentoForm(instituicao=INSTITUICAO)
    return render(request, 'parcial/cadastro_atendimento_form.html', {
        'form': form,
        'instituicao': INSTITUICAO,
    })


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO_PERMISSAO])
def cadastro_atendimento_creas_submit(request):
    """Salva atendimento CREAS."""
    if request.method == 'POST':
        form = MunicipioAtendimentoForm(request.POST, instituicao=INSTITUICAO)
        if form.is_valid():
            atendimento = form.save(commit=False)
            atendimento.usuario = request.user
            atendimento.save()
            form.save_m2m()
            return HttpResponse(
                '<script>'
                'exibirPopupSucesso("Atendimento cadastrado com sucesso!", "sucesso");'
                'setTimeout(() => { document.querySelector(".fixed.inset-0").remove(); }, 500);'
                '</script>'
            )
        return render(request, 'parcial/cadastro_atendimento_form.html', {
            'form': form,
            'instituicao': INSTITUICAO,
        })
    return HttpResponse(status=405)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO_PERMISSAO])
def mostra_todos_atendimentos_creas(request):
    """Lista todos os atendimentos do CREAS."""
    grupos = ModeloPenal.objects.filter(
        atendimento__instituicao_responsavel=INSTITUICAO
    ).select_related(
        'usuario', 'atendimento'
    ).prefetch_related(
        'agressores_atendidos'
    ).order_by('-data_atendimento')

    qtd_de_grupos = grupos.count()
    agressores_totais = sum(g.agressores_atendidos.count() for g in grupos)
    agressores_unicos = Agressor_dados.objects.filter(
        agressores_atendidos__in=grupos
    ).distinct().count()
    qtd_mes = grupos.filter(
        data_atendimento__month=timezone.now().month,
        data_atendimento__year=timezone.now().year
    ).count()

    contexto = {
        'title': f'Todos os Atendimentos — {INSTITUICAO}',
        'instituicao': INSTITUICAO,
        'grupos': grupos,
        'qtd_de_grupos': qtd_de_grupos,
        'qtd_de_grupos_mes': qtd_mes,
        'agressores_totais': agressores_totais,
        'agressores_unicos_totais': agressores_unicos,
        'user': request.user,
    }
    return render(request, 'parcial/mostra_todos_atendimentos.html', contexto)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO_PERMISSAO])
def edita_atendimento_creas(request, grupo_id):
    """Edita um atendimento CREAS."""
    try:
        grupo = ModeloPenal.objects.prefetch_related(
            'agressores_atendidos', 'usuario'
        ).get(id=grupo_id)
    except ModeloPenal.DoesNotExist:
        return HttpResponse(
            '<div class="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg text-center">'
            '<p class="text-sm text-red-700">Atendimento não encontrado.</p></div>',
            status=404
        )

    if request.method == 'POST':
        form = MunicipioAtendimentoForm(request.POST, instance=grupo, instituicao=INSTITUICAO)
        if form.is_valid():
            atendimento = form.save(commit=False)
            atendimento.atualizado_por = request.user
            atendimento.save()
            form.save_m2m()
            return HttpResponse(
                '<script>'
                'exibirPopupSucesso("✅ Atendimento atualizado!", "sucesso");'
                'document.getElementById("modal-container").innerHTML = "";'
                'htmx.ajax("GET", "' + reverse('municipio:mostra_todos_atendimentos_creas') + '", '
                '{target: "#lista-grupos", swap: "innerHTML"});'
                '</script>'
            )
        contexto = {'form': form, 'grupo': grupo, 'instituicao': INSTITUICAO, 'user': request.user}
        return render(request, 'parcial/edita_atendimento.html', contexto)

    form = MunicipioAtendimentoForm(instance=grupo, instituicao=INSTITUICAO)
    contexto = {'form': form, 'grupo': grupo, 'instituicao': INSTITUICAO, 'user': request.user}
    return render(request, 'parcial/edita_atendimento.html', contexto)


@login_required(login_url=reverse_lazy('login'))
def buscar_atendimentos_creas_modal(request):
    """Modal de busca por CPF."""
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

                atendimentos = agressor.agressores_atendidos.filter(
                    atendimento__instituicao_responsavel=INSTITUICAO
                ).order_by('-data_atendimento')
                qtd = atendimentos.count()

                if qtd > 0:
                    resultado = (
                        f'<div class="bg-green-50 border border-green-200 rounded-lg p-4">'
                        f'<span class="text-green-700 font-semibold">'
                        f'Nome: {agressor.nome}<br>CPF: {agressor.cpf}<br>'
                        f'Total de atendimentos ({INSTITUICAO}): {qtd}</span>'
                        f'<div class="mt-2 text-sm text-green-600">'
                        f'Último: {atendimentos.first().data_atendimento.strftime("%d/%m/%Y %H:%M")}'
                        f'</div></div>'
                    )
                else:
                    resultado = (
                        f'<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">'
                        f'<span class="text-yellow-700">{agressor.nome} — CPF: {agressor.cpf}<br>'
                        f'Nenhum atendimento no {INSTITUICAO}.</span></div>'
                    )
            except Agressor_dados.DoesNotExist:
                resultado = '<span class="text-red-600">CPF não encontrado.</span>'

    html = render_to_string('parcial/modal_busca_cpf.html', {
        'resultado': resultado,
        'instituicao': INSTITUICAO,
    }, request)
    return HttpResponse(html)


@login_required(login_url=reverse_lazy('login'))
def relatorio_por_cpf_creas_popup(request):
    """Popup de busca para relatório PDF."""
    return render(request, 'parcial/relatorio_por_cpf_popup.html', {
        'instituicao': INSTITUICAO,
    })


@login_required(login_url=reverse_lazy('login'))
def gerar_relatorio_creas_por_cpf(request):
    """Gera relatório PDF por CPF/nome filtrado pelo CREAS."""
    busca = request.GET.get('busca', '').strip()
    if not busca:
        return HttpResponse('Nenhum termo informado.', status=400)

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

    if not agressor:
        return HttpResponse(f'Nenhum registro encontrado para: "{busca}"', status=404)

    atendimentos = ModeloPenal.objects.filter(
        agressores_atendidos=agressor,
        atendimento__instituicao_responsavel=INSTITUICAO,
    ).select_related('usuario', 'atendimento', 'atualizado_por').order_by('-data_atendimento')

    # === PDF ===
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=3*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    agora = timezone.localtime(timezone.now())

    est_cab = ParagraphStyle('Cab', parent=styles['Normal'], fontName='Helvetica-Bold',
                             fontSize=12, alignment=TA_CENTER, spaceAfter=2,
                             textColor=colors.HexColor('#0d9488'))
    est_sub = ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica',
                             fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#4a4a4a'))
    est_subtit = ParagraphStyle('SubT', parent=styles['Normal'], fontName='Helvetica',
                                fontSize=8, alignment=TA_CENTER, textColor=colors.gray, spaceAfter=6)
    est_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontSize=11,
                               alignment=TA_JUSTIFY, firstLineIndent=2*cm, spaceAfter=10, leading=16)
    est_corpo_sr = ParagraphStyle('CorpoSR', parent=styles['Normal'], fontSize=11,
                                  alignment=TA_JUSTIFY, spaceAfter=10, leading=16)
    est_secao = ParagraphStyle('Secao', parent=styles['Normal'], fontName='Helvetica-Bold',
                               fontSize=9, textColor=colors.HexColor('#0d9488'),
                               spaceAfter=6, spaceBefore=12)
    est_assunto = ParagraphStyle('Assunto', parent=styles['Normal'], fontName='Helvetica-Bold',
                                 fontSize=10, alignment=TA_CENTER, spaceAfter=4,
                                 textColor=colors.HexColor('#0d9488'))
    est_assin = ParagraphStyle('Assin', parent=styles['Normal'], fontName='Helvetica-Bold',
                               fontSize=10, alignment=TA_CENTER)
    est_cargo = ParagraphStyle('Cargo', parent=styles['Normal'], fontName='Helvetica',
                               fontSize=8, alignment=TA_CENTER, textColor=colors.gray)
    est_rodape = ParagraphStyle('Rodape', parent=styles['Normal'], fontName='Helvetica',
                                fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor('#999'))

    elementos = []

    # Cabeçalho
    elementos.append(Paragraph(
        'PLATAFORMA INTEGRADA DE ENFRENTAMENTO À VIOLÊNCIA<br/>DOMÉSTICA E CRIMES SEXUAIS', est_cab))
    elementos.append(Paragraph(f'{INSTITUICAO} — Relatório Individual de Atendimentos', est_sub))
    elementos.append(Paragraph('PIEVDCS — Sistema de Gestão Integrada', est_subtit))
    elementos.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#0d9488'), spaceAfter=20))

    # Identificação
    meses = {'January':'janeiro','February':'fevereiro','March':'março','April':'abril',
             'May':'maio','June':'junho','July':'julho','August':'agosto',
             'September':'setembro','October':'outubro','November':'novembro','December':'dezembro'}
    data_str = agora.strftime('%d de %B de %Y')
    for eng, pt in meses.items():
        data_str = data_str.replace(eng, pt)

    est_esq = ParagraphStyle('Esq', parent=styles['Normal'], fontName='Helvetica-Bold',
                             fontSize=11, textColor=colors.HexColor('#0d9488'))
    est_dir = ParagraphStyle('Dir', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT)

    tabela_id = Table([[
        Paragraph(f'RELATÓRIO Nº {agressor.id}/{agora.strftime("%Y")}', est_esq),
        Paragraph(data_str, est_dir),
    ]], colWidths=[8*cm, 7.7*cm])
    tabela_id.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    elementos.append(tabela_id)
    elementos.append(Spacer(1, 12))

    # Assunto
    elementos.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=4))
    elementos.append(Paragraph(f'ASSUNTO: Relatório de Atendimentos — {agressor.nome}', est_assunto))
    elementos.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=16))

    # Dados do acompanhado
    elementos.append(Paragraph('DADOS DO ACOMPANHADO', est_secao))
    dados_pessoa = [['Nome Completo:', agressor.nome], ['CPF:', agressor.cpf]]
    if hasattr(agressor, 'data_nascimento') and agressor.data_nascimento:
        dados_pessoa.append(['Data de Nascimento:', agressor.data_nascimento.strftime('%d/%m/%Y')])

    tb_pessoa = Table(dados_pessoa, colWidths=[5*cm, 10.7*cm])
    tb_pessoa.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9), ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#555')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5), ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#eee')),
    ]))
    elementos.append(tb_pessoa)
    elementos.append(Spacer(1, 16))

    # Corpo
    qtd = atendimentos.count()
    elementos.append(Paragraph(
        f'Informamos que o(a) acompanhado(a) <b>{agressor.nome}</b>, CPF <b>{agressor.cpf}</b>, '
        f'possui <b>{qtd}</b> atendimento(s) registrado(s) no <b>{INSTITUICAO}</b>.', est_corpo))
    elementos.append(Spacer(1, 8))

    # Tabela de atendimentos
    elementos.append(Paragraph('HISTÓRICO DE ATENDIMENTOS', est_secao))
    dados_tb = [['#', 'Data', 'Setor', 'Tipo', 'Duração', 'Profissional']]
    for i, at in enumerate(atendimentos, 1):
        dados_tb.append([
            str(i), at.data_atendimento.strftime('%d/%m/%Y %H:%M'), at.setor_atendimento,
            str(at.atendimento) if at.atendimento else '—',
            str(at.tempo_atendimento) if at.tempo_atendimento else '—',
            at.usuario.get_full_name() if at.usuario else '—',
        ])
    if qtd == 0:
        dados_tb.append(['', '', 'Nenhum atendimento registrado', '', '', ''])

    tb_at = Table(dados_tb, colWidths=[0.8*cm, 3*cm, 3*cm, 3.5*cm, 2.2*cm, 3.2*cm])
    tb_at.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d9488')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 7),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8), ('TOPPADDING', (0,0), (-1,0), 8),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5), ('TOPPADDING', (0,1), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
    ]))
    elementos.append(tb_at)
    elementos.append(Spacer(1, 12))

    # Avaliações
    com_avaliacao = atendimentos.exclude(avaliacao__isnull=True).exclude(avaliacao='')
    if com_avaliacao.exists():
        elementos.append(Paragraph('AVALIAÇÕES DOS ATENDIMENTOS', est_secao))
        for at in com_avaliacao:
            elementos.append(Paragraph(
                f'<b>Atendimento nº {at.id} — {at.data_atendimento.strftime("%d/%m/%Y")}:</b>', est_corpo_sr))
            elementos.append(Paragraph(at.avaliacao.replace('\n', '<br/>'), est_corpo_sr))

    # Fechamento
    elementos.append(Paragraph(
        'Sem mais para o momento, colocamo-nos à disposição para eventuais esclarecimentos.', est_corpo))
    elementos.append(Paragraph('Atenciosamente,', est_corpo_sr))
    elementos.append(Spacer(1, 40))

    usuario_gerou = request.user.get_full_name() or request.user.username
    elementos.append(HRFlowable(width='50%', thickness=0.5, color=colors.black))
    elementos.append(Paragraph(usuario_gerou, est_assin))
    elementos.append(Paragraph(f'{INSTITUICAO} — PIEVDCS', est_cargo))
    elementos.append(Spacer(1, 20))
    elementos.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=4))
    elementos.append(Paragraph(
        f'Documento gerado em {agora.strftime("%d/%m/%Y %H:%M")} por {usuario_gerou}', est_rodape))
    elementos.append(Paragraph('PIEVDCS — Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais', est_rodape))

    doc.build(elementos)
    buffer.seek(0)
    nome_arq = agressor.cpf.replace('.', '').replace('-', '')
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_creas_{nome_arq}.pdf"'
    return response


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO_PERMISSAO])
def gerar_relatorio_atendimento_creas(request, grupo_id):
    """Gera PDF de um atendimento individual."""
    try:
        grupo = ModeloPenal.objects.select_related(
            'usuario', 'atendimento', 'atualizado_por'
        ).prefetch_related('agressores_atendidos').get(id=grupo_id)
    except ModeloPenal.DoesNotExist:
        return HttpResponse('Atendimento não encontrado.', status=404)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=3*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    agora = timezone.localtime(timezone.now())

    # Estilos (cor teal para CREAS)
    cor = '#0d9488'
    est_cab = ParagraphStyle('Cab2', parent=styles['Normal'], fontName='Helvetica-Bold',
                             fontSize=12, alignment=TA_CENTER, spaceAfter=2, textColor=colors.HexColor(cor))
    est_sub = ParagraphStyle('Sub2', parent=styles['Normal'], fontName='Helvetica',
                             fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#4a4a4a'))
    est_subtit = ParagraphStyle('SubT2', parent=styles['Normal'], fontName='Helvetica',
                                fontSize=8, alignment=TA_CENTER, textColor=colors.gray, spaceAfter=6)
    est_corpo = ParagraphStyle('Corpo2', parent=styles['Normal'], fontSize=11,
                               alignment=TA_JUSTIFY, firstLineIndent=2*cm, spaceAfter=10, leading=16)
    est_corpo_sr = ParagraphStyle('CorpoSR2', parent=est_corpo, firstLineIndent=0)
    est_secao = ParagraphStyle('Secao2', parent=styles['Normal'], fontName='Helvetica-Bold',
                               fontSize=9, textColor=colors.HexColor(cor), spaceAfter=6, spaceBefore=12)
    est_assunto = ParagraphStyle('Assunto2', parent=styles['Normal'], fontName='Helvetica-Bold',
                                 fontSize=10, alignment=TA_CENTER, spaceAfter=4, textColor=colors.HexColor(cor))
    est_assin = ParagraphStyle('Assin2', parent=styles['Normal'], fontName='Helvetica-Bold',
                               fontSize=10, alignment=TA_CENTER)
    est_cargo = ParagraphStyle('Cargo2', parent=styles['Normal'], fontName='Helvetica',
                               fontSize=8, alignment=TA_CENTER, textColor=colors.gray)
    est_rodape = ParagraphStyle('Rodape2', parent=styles['Normal'], fontName='Helvetica',
                                fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor('#999'))

    elementos = []

    elementos.append(Paragraph(
        'PLATAFORMA INTEGRADA DE ENFRENTAMENTO À VIOLÊNCIA<br/>DOMÉSTICA E CRIMES SEXUAIS', est_cab))
    elementos.append(Paragraph(f'{INSTITUICAO} — Atendimento', est_sub))
    elementos.append(Paragraph('PIEVDCS — Sistema de Gestão Integrada', est_subtit))
    elementos.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor(cor), spaceAfter=20))

    meses = {'January':'janeiro','February':'fevereiro','March':'março','April':'abril',
             'May':'maio','June':'junho','July':'julho','August':'agosto',
             'September':'setembro','October':'outubro','November':'novembro','December':'dezembro'}
    data_str = agora.strftime('%d de %B de %Y')
    for eng, pt in meses.items():
        data_str = data_str.replace(eng, pt)

    est_esq = ParagraphStyle('Esq2', parent=styles['Normal'], fontName='Helvetica-Bold',
                             fontSize=11, textColor=colors.HexColor(cor))
    est_dir = ParagraphStyle('Dir2', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT)

    tabela_id = Table([[
        Paragraph(f'OFÍCIO Nº {grupo.id}/{agora.strftime("%Y")}', est_esq),
        Paragraph(data_str, est_dir),
    ]], colWidths=[8*cm, 7.7*cm])
    tabela_id.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                                   ('BOTTOMPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0)]))
    elementos.append(tabela_id)
    elementos.append(Spacer(1, 12))

    elementos.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=4))
    elementos.append(Paragraph(f'ASSUNTO: Relatório de Atendimento — Registro nº {grupo.id}', est_assunto))
    elementos.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=16))

    data_atend = grupo.data_atendimento.strftime('%d/%m/%Y')
    hora_atend = grupo.data_atendimento.strftime('%H:%M')
    tipo_txt = f', com a temática <b>{grupo.atendimento}</b>' if grupo.atendimento else ''
    dur_txt = f', com duração de <b>{grupo.tempo_atendimento}</b>' if grupo.tempo_atendimento else ''

    elementos.append(Paragraph(
        f'Comunicamos que no dia <b>{data_atend}</b>, às <b>{hora_atend}</b>, '
        f'foi realizado atendimento no setor de <b>{grupo.setor_atendimento}</b>{tipo_txt}{dur_txt}.', est_corpo))

    participantes = grupo.agressores_atendidos.all()
    qtd = participantes.count()
    elementos.append(Paragraph(
        f'O atendimento contou com <b>{qtd}</b> participante(s):', est_corpo))
    elementos.append(Spacer(1, 8))

    dados_tb = [['#', 'Nome Completo', 'CPF']]
    for i, ag in enumerate(participantes, 1):
        dados_tb.append([str(i), ag.nome, ag.cpf])
    if qtd == 0:
        dados_tb.append(['', 'Nenhum participante registrado', ''])

    tb = Table(dados_tb, colWidths=[1.2*cm, 10*cm, 4.5*cm])
    tb.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(cor)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 8), ('TOPPADDING', (0,0), (-1,0), 8),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6), ('TOPPADDING', (0,1), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
    ]))
    elementos.append(tb)
    elementos.append(Spacer(1, 12))

    if grupo.avaliacao:
        elementos.append(Paragraph('AVALIAÇÃO DO ATENDIMENTO', est_secao))
        elementos.append(Paragraph(grupo.avaliacao.replace('\n', '<br/>'), est_corpo_sr))

    elementos.append(Paragraph('INFORMAÇÕES COMPLEMENTARES', est_secao))
    profissional = grupo.usuario.get_full_name() or grupo.usuario.username if grupo.usuario else '—'
    criado = grupo.criado_em.strftime('%d/%m/%Y %H:%M') if grupo.criado_em else '—'
    info = [['Profissional:', profissional], ['Data de Registro:', criado]]
    if grupo.atualizado_por:
        nome_at = grupo.atualizado_por.get_full_name() or grupo.atualizado_por.username
        data_at = grupo.atualizado_em.strftime('%d/%m/%Y %H:%M') if grupo.atualizado_em else ''
        info.append(['Última Atualização:', f'{data_at} por {nome_at}'])

    tb_info = Table(info, colWidths=[5.5*cm, 10.2*cm])
    tb_info.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9), ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#555')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#ddd')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#eee')),
    ]))
    elementos.append(tb_info)
    elementos.append(Spacer(1, 20))

    elementos.append(Paragraph('Sem mais, colocamo-nos à disposição.', est_corpo))
    elementos.append(Paragraph('Atenciosamente,', est_corpo_sr))
    elementos.append(Spacer(1, 40))

    elementos.append(HRFlowable(width='50%', thickness=0.5, color=colors.black))
    elementos.append(Paragraph(profissional, est_assin))
    elementos.append(Paragraph(f'{INSTITUICAO} — PIEVDCS', est_cargo))
    elementos.append(Spacer(1, 20))

    usuario_gerou = request.user.get_full_name() or request.user.username
    elementos.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=4))
    elementos.append(Paragraph(f'Documento gerado em {agora.strftime("%d/%m/%Y %H:%M")} por {usuario_gerou}', est_rodape))
    elementos.append(Paragraph('PIEVDCS — Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais', est_rodape))

    doc.build(elementos)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="oficio_creas_{grupo_id}.pdf"'
    return response