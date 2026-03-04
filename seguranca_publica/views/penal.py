#-- coding: utf-8 --
"""
    Modelos de visualizações do sistema Penal
    dir: seguranca_publica/views/penal.py
    @author: OgliariNatan
"""
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from .permission_group import grupos_permitidos
from django.template.loader import render_to_string
from django.db.models import Func, F, Value, CharField, Q
from ..forms.penal import TipoAtendimentoForm, ModeloPenalForm
from ..models.penal import tipo_atendimento, ModeloPenal
from sistema_justica.models.base import Agressor_dados
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
from usuarios.models import CustomUser
from django.contrib.auth.models import Group as CustomGroup
from django.utils import timezone
from datetime import timedelta, date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
import io

ANO_CORRENTE = date.today().year

""" Configuraçao de decoradores para debug """
import os

var_debug = os.getenv('DEBUG', False) #Carrega apenas a variavel de debug

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
@grupos_permitidos(['Polícia Penal'])
def penal(request):

    try:
        notificacao_nao_lida = Notificacao.contar_nao_lidas_usuario(request.user)
    except Exception as e:
        if var_debug == 'True':
            print(f'Tipo de erro:{type(e).__name__}')
            print(f"Erro ao contar notificações não lidas: {e}")
        notificacao_nao_lida = 0

    now = timezone.now()
    first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(seconds=1)

    # Atendimentos deste mês

    try:
        atendimentos_mes = ModeloPenal.objects.filter(
            usuario=request.user,
            data_atendimento__gte=first_day_this_month,
            data_atendimento__lte=now
        ).count()

        # Atendimentos do mês anterior
        atendimentos_mes_anterior = ModeloPenal.objects.filter(
            #usuario=request.user,
            data_atendimento__gte=first_day_last_month,
            data_atendimento__lte=last_day_last_month
        ).count()

        # Cálculo da variação percentual
        if atendimentos_mes_anterior > 0:
            variacao = ((atendimentos_mes - atendimentos_mes_anterior) / atendimentos_mes_anterior) * 100
        else:
            variacao = 100 if atendimentos_mes > 0 else 0
        
        # Lista de atendimentos com participantes
        atendimentos = ModeloPenal.objects.filter(usuario=request.user).order_by('-id')
        grupos = []
        for atendimento in atendimentos:
            grupos.append({
                'id': atendimento.id,
                'nome': f'Atendimento {atendimento.id} - {atendimento.data_atendimento:%d/%m/%Y %H:%M}',
                'qtd_agressores': atendimento.agressores_atendidos.count(),
                'participantes': atendimento.agressores_atendidos.all(),
            })
            
    except Exception as e:
        if var_debug == 'True':
            print(f'Tipo de erro:{type(e).__name__}')
            print(f"Erro ao buscar atendimentos: {e}")
        atendimentos_mes = 0
        atendimentos_mes_anterior = 0
        variacao = 0
        grupos = []

    casos_ativos= (256, '+12')
    tipo_atendimentos = tipo_atendimento.objects.count()

    contexto = {
        'title': 'Polícia Penal',
        'description': 'This page provides information about the penal system.',
        'ano_corrente': ANO_CORRENTE,
        'encaminhamentos': 5,
        'alert': notificacao_nao_lida,
        'qtd_atendimentos': atendimentos_mes,
        'qtd_atendimentos_anterior': atendimentos_mes_anterior,
        'variacao_atendimentos': variacao,
        'tipo_atendimentos': tipo_atendimentos,
        'grupos': grupos,
        'user': request.user,
        'casos_ativos': casos_ativos[0],
        'casos_ativos_percent': casos_ativos[1],
    }
    return render(request, "penal.html", contexto)
   



@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def cadastro_tipo_atendimento_form(request):
    form = TipoAtendimentoForm()
    return render(request, 'parcial/cadastro_tipo_atendimento_form.html', {'form': form})

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def cadastro_tipo_atendimento_submit(request):
    if request.method == 'POST':
        form = TipoAtendimentoForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("""
                <script>
                    exibirPopupSucesso('Tipo de atendimento cadastrado com sucesso!', 'sucesso');
                    setTimeout(() => {
                        document.querySelector('.fixed.inset-0').remove();
                    }, 500);
                </script>
            """)
        else:
            return render(request, 'parcial/cadastro_tipo_atendimento_form.html', {'form': form})
    return HttpResponse(status=405)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def cadastro_atendimento_penal_form(request):
    form = ModeloPenalForm()
    return render(request, 'parcial/cadastro_atendimento_penal_form.html', {'form': form})

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def cadastro_atendimento_penal_submit(request):
    if request.method == 'POST':
        form = ModeloPenalForm(request.POST)
        if form.is_valid():
            atendimento = form.save(commit=False)
            atendimento.usuario = request.user
            atendimento.save()
            form.save_m2m()  # Salvar relações many-to-many
            return HttpResponse("""
                <script>
                    exibirPopupSucesso('Atendimento cadastrado com sucesso!', 'sucesso');
                    setTimeout(() => {
                        document.querySelector('.fixed.inset-0').remove();
                    }, 500);
                </script>
            """)
        else:
            return render(request, 'parcial/cadastro_atendimento_penal_form.html', {'form': form})
    return HttpResponse(status=405)


@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def buscar_atendimentos_por_cpf_modal(request):
    """Busca atendimentos por CPF e exibe no modal com visualização detalhada."""
    if var_debug == 'True':
        print("Buscando atendimentos por CPF no modal...")

    agressor = None
    atendimentos = None
    qtd = 0
    erro = ""

    if request.method == "POST":
        cpf = request.POST.get('cpf', '').replace('.', '').replace('-', '').strip()
        if not cpf:
            erro = "CPF não informado."
        else:
            try:
                agressor = Agressor_dados.objects.annotate(
                    cpf_limpo=Func(
                        Func(F('cpf'), Value('.'), Value(''), function='replace'),
                        Value('-'), Value(''),
                        function='replace', output_field=CharField()
                    )
                ).get(cpf_limpo=cpf)

                atendimentos = ModeloPenal.objects.filter(
                    agressores_atendidos=agressor
                ).select_related(
                    'usuario', 'atendimento'
                ).prefetch_related(
                    'agressores_atendidos'
                ).order_by('-data_atendimento')

                qtd = atendimentos.count()

            except Agressor_dados.DoesNotExist:
                erro = "CPF não encontrado na base de dados."

    contexto = {
        'agressor': agressor,
        'atendimentos': atendimentos,
        'qtd': qtd,
        'erro': erro,
    }
    return render(request, 'parcial/modal_busca_cpf.html', contexto)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def mostra_todos_grupos_penal(request):
    """
        Mostra todos os grupos de atendimentos registrados no sistema Penal
        Viualização CRÍTICA.
    """
    if not request.user.has_perm('seguranca_publica.view_modelopenal'):
        raise ValueError("Usuário não tem permissão para visualizar os atendimentos penais.")

    grupos = ModeloPenal.objects.select_related(
        'usuario',
        'atendimento'
    ).prefetch_related(
        'agressores_atendidos'
    ).order_by('-data_atendimento')

    qtd_de_grupos = grupos.count()

    quantidades_atendidos = sum([grupo.agressores_atendidos.count() for grupo in grupos])

    quantidades_atendidos_unicos = Agressor_dados.objects.filter(
        agressores_atendidos__in=grupos
    ).distinct().count()
    

    qtd_de_grupos_mes = grupos.filter(
        data_atendimento__month=timezone.now().month,
        data_atendimento__year=timezone.now().year
    ).count()


    contexto = {
        'title': 'Todos os Atendimentos - Polícia Penal',
        'description': 'Lista completa de todos os atendimentos registrados pela Polícia Penal.',
        'ano_corrente': ANO_CORRENTE,
        'grupos': grupos,
        'qtd_de_grupos': qtd_de_grupos,
        'qtd_de_grupos_mes': qtd_de_grupos_mes,
        'agressores_totais': quantidades_atendidos,
        'agressores_unicos_totais': quantidades_atendidos_unicos,
        'user': request.user,
    }
    return render(request, "parcial/mostra_todos_grupos.html", contexto)



@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def edita_atendimento_pp(request, grupo_id):
    """
    Edita um atendimento penal específico via HTMX.
    """
    try:
        grupo = ModeloPenal.objects.prefetch_related('agressores_atendidos', 'usuario').get(id=grupo_id)
    except ModeloPenal.DoesNotExist:
        return HttpResponse(
            '<div class="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg text-center">'
            '<p class="text-sm text-red-700"><i class="fas fa-exclamation-triangle mr-2"></i>'
            'Atendimento não encontrado.</p></div>',
            status=404
        )

    if request.method == 'POST':
        form = ModeloPenalForm(request.POST, instance=grupo)
        if form.is_valid():
            atendimento = form.save(commit=False)
            atendimento.usuario = request.user
            atendimento.atualizado_por = request.user
            atendimento.save()
            form.save_m2m()
            
            # Retornar script que fecha modal e mostra sucesso
            return HttpResponse(
                '<script>'
                'exibirPopupSucesso("✅ Atendimento atualizado com sucesso!", "sucesso");'
                'document.getElementById("modal-container").innerHTML = "";'
                'htmx.ajax("GET", "' + reverse('seguranca_publica:mostra_todos_grupos_penal') + '", '
                '{target: "#lista-grupos", swap: "innerHTML"});'
                '</script>'
            )
        else:
            # Re-renderizar modal com erros
            contexto = {
                'title': f'Editar Atendimento #{grupo_id}',
                'form': form,
                'grupo': grupo,
                'user': request.user,
            }
            return render(request, 'parcial/penal/edita_atendimento.html', contexto)
    
    else:  # GET request - renderizar modal
        form = ModeloPenalForm(instance=grupo)

    contexto = {
        'title': f'Editar Atendimento #{grupo_id}',
        'form': form,
        'grupo': grupo,
        'user': request.user,
    }
    return render(request, 'parcial/penal/edita_atendimento.html', contexto)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def gerar_relatorio_atendimento(request, grupo_id):
    """Gera relatório em PDF no formato de ofício usando ReportLab."""
    try:
        grupo = ModeloPenal.objects.select_related(
            'usuario', 'atendimento', 'atualizado_por'
        ).prefetch_related('agressores_atendidos').get(id=grupo_id)
    except ModeloPenal.DoesNotExist:
        return HttpResponse('Atendimento não encontrado.', status=404)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=3 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
    )

    # Estilos
    styles = getSampleStyleSheet()

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
    estilo_oficio = ParagraphStyle(
        'Oficio', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11,
        alignment=TA_RIGHT, textColor=colors.HexColor('#1e3a5f'),
    )
    estilo_data = ParagraphStyle(
        'Data', parent=styles['Normal'],
        fontSize=10, alignment=TA_RIGHT, spaceAfter=12,
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
        'CorpoSemRecuo', parent=estilo_corpo,
        firstLineIndent=0,
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

    # Elementos do documento
    elementos = []

    # === Cabeçalho institucional ===
    elementos.append(Paragraph(
        'PLATAFORMA INTEGRADA DE ENFRENTAMENTO À VIOLÊNCIA<br/>DOMÉSTICA E CRIMES SEXUAIS',
        estilo_cabecalho
    ))
    elementos.append(Paragraph('Polícia Penal — Grupos Reflexivos', estilo_subcabecalho))
    elementos.append(Paragraph('PIEVDCS — Sistema de Gestão Integrada', estilo_subtitulo_cab))
    elementos.append(HRFlowable(
        width='100%', thickness=2,
        color=colors.HexColor('#1e3a5f'), spaceAfter=20,
    ))

    # === Identificação do ofício ===
    agora = timezone.localtime(timezone.now())

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
        'IdEsq2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11,
        textColor=colors.HexColor('#122239'),
    )
    estilo_id_dir = ParagraphStyle(
        'IdDir2', parent=styles['Normal'],
        fontSize=10, alignment=TA_RIGHT,
    )

    tabela_id = Table(
        [[
            Paragraph(f'OFÍCIO Nº {grupo.id}/{agora.strftime("%Y")}', estilo_id_esq),
            Paragraph(data_str, estilo_id_dir),
        ]],
        colWidths=[8 * cm, 7.7 * cm]
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
        f'ASSUNTO: Relatório de Atendimento em Grupo/Individual Reflexivo — Registro nº {grupo.id}',
        estilo_assunto
    ))
    elementos.append(HRFlowable(
        width='100%', thickness=0.5, color=colors.HexColor('#ddd'),
        spaceBefore=0, spaceAfter=16,
    ))

    # === Corpo do ofício ===
    data_atend = grupo.data_atendimento.strftime('%d/%m/%Y')
    hora_atend = grupo.data_atendimento.strftime('%H:%M')
    tipo_texto = f', com a temática <b>{grupo.atendimento}</b>' if grupo.atendimento else ''
    duracao_texto = f', com duração de <b>{grupo.tempo_atendimento}</b>' if grupo.tempo_atendimento else ''

    elementos.append(Paragraph(
        f'Comunicamos, para os devidos fins, que no dia <b>{data_atend}</b>, '
        f'às <b>{hora_atend}</b>, foi realizado atendimento no setor de '
        f'<b>{grupo.setor_atendimento}</b>{tipo_texto}{duracao_texto}.',
        estilo_corpo
    ))

    participantes = grupo.agressores_atendidos.all()
    qtd = participantes.count()

    elementos.append(Paragraph(
        f'O atendimento contou com a participação de <b>{qtd}</b> pessoa(s), '
        f'conforme relação abaixo:',
        estilo_corpo
    ))
    elementos.append(Spacer(1, 8))

    # === Tabela de participantes ===
    dados_tabela = [['ID', 'Nome Completo', 'CPF']]
    for i, ag in enumerate(participantes, 1):
        dados_tabela.append([str(i), ag.nome, ag.cpf])

    if qtd == 0:
        dados_tabela.append(['', 'Nenhum participante registrado', ''])

    tabela = Table(dados_tabela, colWidths=[1.2 * cm, 10 * cm, 4.5 * cm])
    tabela.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5d5d5d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        # Corpo
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ]))
    elementos.append(tabela)
    elementos.append(Spacer(1, 12))

    # === Avaliação ===
    if grupo.avaliacao:
        elementos.append(Paragraph('AVALIAÇÃO DO ATENDIMENTO', estilo_secao))
        elementos.append(Paragraph(grupo.avaliacao.replace('\n', '<br/>'), estilo_corpo_sem_recuo))
        elementos.append(Spacer(1, 8))

    # === Informações complementares ===
    elementos.append(Paragraph('INFORMAÇÕES COMPLEMENTARES', estilo_secao))
    profissional = grupo.usuario.get_full_name() or grupo.usuario.username if grupo.usuario else '—'
    criado = grupo.criado_em.strftime('%d/%m/%Y %H:%M') if grupo.criado_em else '—'

    info_dados = [
        ['Profissional Responsável:', profissional],
        ['Data de Registro:', criado],
    ]
    if grupo.atualizado_por:
        atualizado_nome = grupo.atualizado_por.get_full_name() or grupo.atualizado_por.username
        atualizado_data = grupo.atualizado_em.strftime('%d/%m/%Y %H:%M') if grupo.atualizado_em else ''
        info_dados.append(['Última Atualização:', f'{atualizado_data} por {atualizado_nome}'])

    info_tabela = Table(info_dados, colWidths=[5.5 * cm, 10.2 * cm])
    info_tabela.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#eeeeee')),
    ]))
    elementos.append(info_tabela)
    elementos.append(Spacer(1, 20))

    # === Fechamento ===
    elementos.append(Paragraph(
        'Sem mais para o momento, colocamo-nos à disposição para '
        'eventuais esclarecimentos que se façam necessários.',
        estilo_corpo
    ))
    elementos.append(Paragraph('Atenciosamente,', estilo_corpo_sem_recuo))
    elementos.append(Spacer(1, 40))

    # === Assinatura ===
    elementos.append(HRFlowable(width='50%', thickness=0.5, color=colors.black))
    elementos.append(Paragraph(profissional, estilo_assinatura))
    elementos.append(Paragraph('Instituição: Polícia Penal', estilo_cargo))
    elementos.append(Spacer(1, 20))

    # === Marca d'água de geração ===
    usuario_gerou = request.user.get_full_name() or request.user.username
    elementos.append(HRFlowable(
        width='100%', thickness=0.5, color=colors.HexColor('#ddd'), spaceAfter=4
    ))
    elementos.append(Paragraph(
        f'Documento gerado em {agora.strftime("%d/%m/%Y %H:%M")} por {usuario_gerou}',
        estilo_rodape
    ))
    elementos.append(Paragraph(
        'PIEVDCS — Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais',
        estilo_rodape
    ))

    # Gerar PDF
    doc.build(elementos)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="oficio_atendimento_{grupo_id}.pdf"'
    return response

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def relatorio_por_cpf_popup(request):
    """Renderiza o popup de busca por CPF/Nome para gerar relatório PDF."""
    return render(request, 'parcial/penal/relatorio_por_cpf_popup.html')


@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def gerar_relatorio_por_cpf(request):
    """
    Gera relatório PDF com todos os atendimentos de um agressor,
    buscando por CPF ou nome.
    """
    busca = request.GET.get('busca', '').strip()
    if not busca:
        return HttpResponse('Nenhum termo informado.', status=400)

    # Tenta buscar por CPF (remove pontuação)
    busca_limpa = busca.replace('.', '').replace('-', '').replace(' ', '')

    agressor = None
    if busca_limpa.isdigit() and len(busca_limpa) == 11:
        # Busca por CPF
        agressor = Agressor_dados.objects.annotate(
            cpf_limpo=Func(
                Func(F('cpf'), Value('.'), Value(''), function='replace'),
                Value('-'), Value(''),
                function='replace', output_field=CharField()
            )
        ).filter(cpf_limpo=busca_limpa).first()
    
    if not agressor:
        # Busca por nome (parcial, case-insensitive)
        agressor = Agressor_dados.objects.filter(nome__icontains=busca).first()

    if not agressor:
        return HttpResponse(
            f'Nenhum agressor encontrado para: "{busca}"', status=404
        )

    # Busca todos os atendimentos deste agressor
    atendimentos = ModeloPenal.objects.filter(
        agressores_atendidos=agressor
    ).select_related(
        'usuario', 'atendimento', 'atualizado_por'
    ).order_by('-data_atendimento')

    # === Geração do PDF ===
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=3 * cm, rightMargin=2 * cm,
        topMargin=2.5 * cm, bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    estilo_cabecalho = ParagraphStyle(
        'Cab', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12,
        alignment=TA_CENTER, spaceAfter=2,
        textColor=colors.HexColor('#1e3a5f'),
    )
    estilo_subcabecalho = ParagraphStyle(
        'SubCab', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10,
        alignment=TA_CENTER, textColor=colors.HexColor('#4a4a4a'),
    )
    estilo_subtitulo = ParagraphStyle(
        'SubTit', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8,
        alignment=TA_CENTER, textColor=colors.gray, spaceAfter=6,
    )
    estilo_oficio = ParagraphStyle(
        'Oficio', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11,
        alignment=TA_RIGHT, textColor=colors.HexColor('#1e3a5f'),
    )
    estilo_data = ParagraphStyle(
        'Data', parent=styles['Normal'],
        fontSize=10, alignment=TA_RIGHT, spaceAfter=12,
    )
    estilo_assunto = ParagraphStyle(
        'Assunto', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10,
        leftIndent=12, spaceAfter=16,
        textColor=colors.HexColor('#1e3a5f'),
    )
    estilo_corpo = ParagraphStyle(
        'Corpo', parent=styles['Normal'],
        fontSize=11, alignment=TA_JUSTIFY,
        firstLineIndent=2 * cm, spaceAfter=10, leading=16,
    )
    estilo_corpo_sem_recuo = ParagraphStyle(
        'CorpoSR', parent=styles['Normal'],
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
        'Assin', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER,
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

    elementos = []
    agora = timezone.localtime(timezone.now())

    # === Cabeçalho institucional ===
    elementos.append(Paragraph(
        'PLATAFORMA INTEGRADA DE ENFRENTAMENTO À VIOLÊNCIA<br/>'
        'DOMÉSTICA E CRIMES SEXUAIS', estilo_cabecalho
    ))
    elementos.append(Paragraph(
        'Polícia Penal — Relatório Individual de Atendimentos', estilo_subcabecalho
    ))
    elementos.append(Paragraph(
        'PIEVDCS — Sistema de Gestão Integrada', estilo_subtitulo
    ))
    elementos.append(HRFlowable(
        width='100%', thickness=2,
        color=colors.HexColor('#1e3a5f'), spaceAfter=20,
    ))

    # === Identificação ===
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
            Paragraph(f'RELATÓRIO Nº {agressor.id}/{agora.strftime("%Y")}', estilo_id_esq),
            Paragraph(data_str, estilo_id_dir),
        ]],
        colWidths=[8 * cm, 7.7 * cm]
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
        f'ASSUNTO: Relatório de Atendimentos individual — {agressor.nome}', estilo_assunto
    ))
    elementos.append(HRFlowable(
        width='100%', thickness=0.5, color=colors.HexColor('#ddd'),
        spaceBefore=0, spaceAfter=16,
    ))

    # === Dados do agressor ===
    elementos.append(Paragraph('DADOS DO ACOMPANHADO', estilo_secao))
    dados_pessoa = [
        ['Nome Completo:', agressor.nome],
        ['CPF:', agressor.cpf],
    ]
    # Adiciona campos extras se existirem
    if hasattr(agressor, 'data_nascimento') and agressor.data_nascimento:
        dados_pessoa.append([
            'Data de Nascimento:',
            agressor.data_nascimento.strftime('%d/%m/%Y')
        ])

    tabela_pessoa = Table(dados_pessoa, colWidths=[5 * cm, 10.7 * cm])
    tabela_pessoa.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#eeeeee')),
    ]))
    elementos.append(tabela_pessoa)
    elementos.append(Spacer(1, 16))

    # === Corpo ===
    qtd = atendimentos.count()
    elementos.append(Paragraph(
        f'Informamos que o acompanhado <b>{agressor.nome}</b>, '
        f'CPF <b>{agressor.cpf}</b>, possui <b>{qtd}</b> atendimento(s) '
        f'registrado(s) na plataforma, conforme detalhamento a seguir:',
        estilo_corpo
    ))
    elementos.append(Spacer(1, 8))

    # === Tabela de atendimentos ===
    estilo_celula = ParagraphStyle(
    'celula_tabela', fontName='Helvetica', fontSize=8, leading=10
    )
    elementos.append(Paragraph('HISTÓRICO DE ATENDIMENTOS', estilo_secao))

    cabecalho_tabela = ['id', 'Data', 'Setor', 'Tipo', 'Duração', 'Profissional']
    dados_tabela = [cabecalho_tabela]

    for i, atend in enumerate(atendimentos, 1):
        data_fmt = atend.data_atendimento.strftime('%d/%m/%Y %H:%M')
        tipo_txt = str(atend.atendimento) if atend.atendimento else '—'
        duracao_txt = str(atend.tempo_atendimento) if atend.tempo_atendimento else '—'
        prof = atend.usuario.get_full_name() if atend.usuario else '—'
        dados_tabela.append([
            str(i),
            data_fmt,
            Paragraph(atend.setor_atendimento or '—', estilo_celula),
            Paragraph(tipo_txt, estilo_celula),
            duracao_txt,
            Paragraph(prof, estilo_celula),
        ])

    if qtd == 0:
        dados_tabela.append(['', '', 'Nenhum atendimento registrado', '', '', ''])

    tabela_atend = Table(
        dados_tabela,
        colWidths=[0.8 * cm, 3 * cm, 3 * cm, 3.5 * cm, 2.2 * cm, 3.2 * cm]
    )
    tabela_atend.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5b5b5b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        # Corpo
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#f9f9f9')]),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ]))
    elementos.append(tabela_atend)
    elementos.append(Spacer(1, 12))

    # === Avaliações individuais ===
    atendimentos_com_avaliacao = atendimentos.exclude(
        avaliacao__isnull=True
    ).exclude(avaliacao='')

    if atendimentos_com_avaliacao.exists():
        elementos.append(Paragraph('AVALIAÇÕES DOS ATENDIMENTOS', estilo_secao))
        for atend in atendimentos_com_avaliacao:
            data_fmt = atend.data_atendimento.strftime('%d/%m/%Y')
            elementos.append(Paragraph(
                f'<b>Atendimento nº {atend.id} — {data_fmt}:</b>',
                estilo_corpo_sem_recuo
            ))
            elementos.append(Paragraph(
                atend.avaliacao.replace('\n', '<br/>'),
                estilo_corpo_sem_recuo
            ))
        elementos.append(Spacer(1, 8))

    # === Fechamento ===
    elementos.append(Paragraph(
        'Sem mais para o momento, colocamo-nos à disposição para '
        'eventuais esclarecimentos que se façam necessários.',
        estilo_corpo
    ))
    elementos.append(Paragraph('Atenciosamente,', estilo_corpo_sem_recuo))
    elementos.append(Spacer(1, 40))

    # === Assinatura ===
    usuario_gerou = request.user.get_full_name() or request.user.username
    elementos.append(HRFlowable(width='50%', thickness=0.5, color=colors.black))
    elementos.append(Paragraph(usuario_gerou, estilo_assinatura))
    elementos.append(Paragraph('Instituição: Polícia Penal', estilo_cargo))
    elementos.append(Spacer(1, 20))

    # === Rodapé ===
    elementos.append(HRFlowable(
        width='100%', thickness=0.5,
        color=colors.HexColor('#ddd'), spaceAfter=4,
    ))
    elementos.append(Paragraph(
        f'Documento gerado em {agora.strftime("%d/%m/%Y %H:%M")} por {usuario_gerou}',
        estilo_rodape
    ))
    elementos.append(Paragraph(
        'PIEVDCS — Plataforma Integrada de Enfrentamento à '
        'Violência Doméstica e Crimes Sexuais',
        estilo_rodape
    ))

    doc.build(elementos)
    buffer.seek(0)

    nome_arquivo = agressor.cpf.replace('.', '').replace('-', '')
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="relatorio_atendimentos_{nome_arquivo}.pdf"'
    )
    return response

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Polícia Penal'])
def consultar_mp_penal(request):
    """
    Lista medidas protetivas com filtros para consulta da Polícia Penal (somente leitura).
    dir: seguranca_publica/views/penal.py
    """
    from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
    from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario

    filtro_status = request.GET.get('status', 'todas')
    filtro_ordenar = request.GET.get('ordenar', 'periodo_mp')
    filtro_busca = request.GET.get('busca', '').strip()
    filtro_comarca = request.GET.get('comarca', '')

    qs = FormularioMedidaProtetiva.objects.select_related(
        'vitima', 'agressor', 'comarca_competente'
    )

    hoje = date.today()

    # Filtro por status
    if filtro_status == 'ativas':
        qs = qs.filter(periodo_mp__gte=hoje)
    elif filtro_status == 'vencidas':
        qs = qs.filter(periodo_mp__lt=hoje)

    # Filtro por comarca
    if filtro_comarca:
        qs = qs.filter(comarca_competente_id=filtro_comarca)

    # Filtro por busca (nome ou CPF da vítima/agressor)
    if filtro_busca:
        qs = qs.filter(
            Q(vitima__nome__icontains=filtro_busca) |
            Q(vitima__cpf__icontains=filtro_busca) |
            Q(agressor__nome__icontains=filtro_busca) |
            Q(agressor__cpf__icontains=filtro_busca)
        )

    # Ordenação
    ordenacoes_permitidas = ['periodo_mp', '-periodo_mp', '-data_solicitacao']
    if filtro_ordenar not in ordenacoes_permitidas:
        filtro_ordenar = 'periodo_mp'
    qs = qs.order_by(filtro_ordenar)

    # Propriedades dinâmicas - ativos primeiro
    medidas = list(qs)
    for mp in medidas:
        mp.ativa = mp.periodo_mp >= hoje
        mp.dias_restantes = (mp.periodo_mp - hoje).days if mp.ativa else 0
    medidas.sort(key=lambda mp: (not mp.ativa,))

    comarcas = ComarcasPoderJudiciario.objects.order_by('nome')

    contexto = {
        'medidas': medidas,
        'filtro_status': filtro_status,
        'filtro_ordenar': filtro_ordenar,
        'filtro_busca': filtro_busca,
        'filtro_comarca': filtro_comarca,
        'comarcas': comarcas,
    }

    # Requisição HTMX com filtro → retorna só a tabela
    if request.headers.get('HX-Target') == 'tabela-mp-penal':
        return render(request, 'parcial/penal/tabela_mp_penal.html', contexto)

    return render(request, 'parcial/penal/consultar_mp.html', contexto)