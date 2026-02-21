# municipio/view/caps.py
"""Views do CAPS — wrappers sobre atendimento_generico."""
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from . import atendimento_generico as gen
import os

if os.getenv('DEBUG') == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo as debug_dec
else:
    debug_dec = lambda f: f

GRUPO = 'CAPS'
CONFIG = {
    'instituicao': 'CAPS',
    'titulo': 'Centros de Atenção Psicossocial',
    'cor_tailwind': 'violet',
    'cor_hex': '#7c3aed',
    'pdf_prefix': 'caps',
    'template_principal': 'caps.html',
    'url_names': {
        'cadastro_form': 'municipio:cadastro_atendimento_caps_form',
        'cadastro_submit': 'municipio:cadastro_atendimento_caps_submit',
        'mostra_todos': 'municipio:mostra_todos_atendimentos_caps',
        'edita': 'municipio:edita_atendimento_caps',
        'buscar_cpf': 'municipio:buscar_atendimentos_caps_modal',
        'relatorio_cpf_popup': 'municipio:relatorio_por_cpf_caps_popup',
        'gerar_relatorio_cpf': 'municipio:gerar_relatorio_caps_por_cpf',
        'relatorio_atendimento': 'municipio:relatorio_atendimento_caps',
    },
}


@debug_dec
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def caps(request):
    return gen.dashboard_instituicao(request, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def cadastro_atendimento_caps_form(request):
    return gen.cadastro_form(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def cadastro_atendimento_caps_submit(request):
    return gen.cadastro_submit(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def mostra_todos_atendimentos_caps(request):
    return gen.mostra_todos(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def edita_atendimento_caps(request, grupo_id):
    return gen.edita_atendimento(request, grupo_id, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
def buscar_atendimentos_caps_modal(request):
    return gen.buscar_cpf_modal(request, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
def relatorio_por_cpf_caps_popup(request):
    return gen.relatorio_cpf_popup(request, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
def gerar_relatorio_caps_por_cpf(request):
    return gen.gerar_relatorio_por_cpf(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def gerar_relatorio_atendimento_caps(request, grupo_id):
    return gen.gerar_relatorio_atendimento(request, grupo_id, CONFIG)