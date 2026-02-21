# municipio/view/secretaria_saude.py
"""Views da Secretaria da Saúde — wrappers sobre atendimento_generico."""
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from . import atendimento_generico as gen
import os

if os.getenv('DEBUG') == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo as debug_dec
else:
    debug_dec = lambda f: f

GRUPO = 'Secretaria da Saúde'
CONFIG = {
    'instituicao': 'Secretaria da Saúde',
    'titulo': 'Secretaria da Saúde',
    'cor_tailwind': 'rose',
    'cor_hex': '#e11d48',
    'pdf_prefix': 'sec_saude',
    'template_principal': 'secretaria_saude.html',
    'url_names': {
        'cadastro_form': 'municipio:cadastro_atendimento_secretaria_saude_form',
        'cadastro_submit': 'municipio:cadastro_atendimento_secretaria_saude_submit',
        'mostra_todos': 'municipio:mostra_todos_atendimentos_secretaria_saude',
        'edita': 'municipio:edita_atendimento_secretaria_saude',
        'buscar_cpf': 'municipio:buscar_atendimentos_secretaria_saude_modal',
        'relatorio_cpf_popup': 'municipio:relatorio_por_cpf_secretaria_saude_popup',
        'gerar_relatorio_cpf': 'municipio:gerar_relatorio_secretaria_saude_por_cpf',
        'relatorio_atendimento': 'municipio:relatorio_atendimento_secretaria_saude',
    },
}


@debug_dec
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def secretaria_saude(request):
    return gen.dashboard_instituicao(request, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def cadastro_atendimento_ss_form(request):
    return gen.cadastro_form(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def cadastro_atendimento_ss_submit(request):
    return gen.cadastro_submit(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def mostra_todos_atendimentos_ss(request):
    return gen.mostra_todos(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def edita_atendimento_ss(request, grupo_id):
    return gen.edita_atendimento(request, grupo_id, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
def buscar_atendimentos_ss_modal(request):
    return gen.buscar_cpf_modal(request, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
def relatorio_por_cpf_ss_popup(request):
    return gen.relatorio_cpf_popup(request, CONFIG)


@debug_dec
@login_required(login_url=reverse_lazy('login'))
def gerar_relatorio_ss_por_cpf(request):
    return gen.gerar_relatorio_por_cpf(request, CONFIG)


@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos([GRUPO])
def gerar_relatorio_atendimento_ss(request, grupo_id):
    return gen.gerar_relatorio_atendimento(request, grupo_id, CONFIG)