# municipio/view/cras.py
"""Views do CRAS — wrappers sobre atendimento_generico."""
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from . import atendimento_generico as gen
import os

# Decorador de debug
if os.getenv('DEBUG') == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo as debug_dec
else:
    debug_dec = lambda f: f

GRUPO = 'CRAS'
CONFIG = {
    'instituicao': 'CRAS',
    'titulo': 'Centros de Referência de Assistência Social',
    'cor_tailwind': 'indigo',
    'cor_hex': '#4f46e5',
    'pdf_prefix': 'cras',
    'template_principal': 'cras.html',
    'url_names': {
        'cadastro_form': 'municipio:cadastro_atendimento_cras_form',
        'cadastro_submit': 'municipio:cadastro_atendimento_cras_submit',
        'mostra_todos': 'municipio:mostra_todos_atendimentos_cras',
        'edita': 'municipio:edita_atendimento_cras',
        'buscar_cpf': 'municipio:buscar_atendimentos_cras_modal',
        'relatorio_cpf_popup': 'municipio:relatorio_por_cpf_cras_popup',
        'gerar_relatorio_cpf': 'municipio:gerar_relatorio_cras_por_cpf',
        'relatorio_atendimento': 'municipio:relatorio_atendimento_cras',
    },
}


@debug_dec
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def cras(request):
    return gen.dashboard_instituicao(request, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def cadastro_atendimento_cras_form(request):
    return gen.cadastro_form(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def cadastro_atendimento_cras_submit(request):
    return gen.cadastro_submit(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def mostra_todos_atendimentos_cras(request):
    return gen.mostra_todos(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def edita_atendimento_cras(request, grupo_id):
    return gen.edita_atendimento(request, grupo_id, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
def buscar_atendimentos_cras_modal(request):
    return gen.buscar_cpf_modal(request, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
def relatorio_por_cpf_cras_popup(request):
    return gen.relatorio_cpf_popup(request, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
def gerar_relatorio_cras_por_cpf(request):
    return gen.gerar_relatorio_por_cpf(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def gerar_relatorio_atendimento_cras(request, grupo_id):
    return gen.gerar_relatorio_atendimento(request, grupo_id, CONFIG)