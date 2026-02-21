# municipio/urls.py
from django.urls import path
from .view.conselho_tutelar import conselho_tutelar
from .view.creas import (
    creas, cadastro_atendimento_creas_form, cadastro_atendimento_creas_submit,
    mostra_todos_atendimentos_creas, edita_atendimento_creas,
    buscar_atendimentos_creas_modal, relatorio_por_cpf_creas_popup,
    gerar_relatorio_creas_por_cpf, gerar_relatorio_atendimento_creas,
)
from .view.cras import (
    cras, cadastro_atendimento_cras_form, cadastro_atendimento_cras_submit,
    mostra_todos_atendimentos_cras, edita_atendimento_cras,
    buscar_atendimentos_cras_modal, relatorio_por_cpf_cras_popup,
    gerar_relatorio_cras_por_cpf, gerar_relatorio_atendimento_cras,
)
from .view.caps import (
    caps, cadastro_atendimento_caps_form, cadastro_atendimento_caps_submit,
    mostra_todos_atendimentos_caps, edita_atendimento_caps,
    buscar_atendimentos_caps_modal, relatorio_por_cpf_caps_popup,
    gerar_relatorio_caps_por_cpf, gerar_relatorio_atendimento_caps,
)
from .view.secretaria_saude import (
    secretaria_saude, cadastro_atendimento_ss_form, cadastro_atendimento_ss_submit,
    mostra_todos_atendimentos_ss, edita_atendimento_ss,
    buscar_atendimentos_ss_modal, relatorio_por_cpf_ss_popup,
    gerar_relatorio_ss_por_cpf, gerar_relatorio_atendimento_ss,
)

app_name = 'municipio'


def _rotas_instituicao(prefix, views, name_prefix):
    """Gera as 9 rotas padrão de uma instituição."""
    return [
        path(f'{prefix}/', views[0], name=name_prefix),
        path(f'{prefix}/cadastro_atendimento_form/', views[1], name=f'cadastro_atendimento_{name_prefix}_form'),
        path(f'{prefix}/cadastro_atendimento_submit/', views[2], name=f'cadastro_atendimento_{name_prefix}_submit'),
        path(f'{prefix}/todos_atendimentos/', views[3], name=f'mostra_todos_atendimentos_{name_prefix}'),
        path(f'{prefix}/edita_atendimento/<int:grupo_id>/', views[4], name=f'edita_atendimento_{name_prefix}'),
        path(f'{prefix}/buscar_cpf_modal/', views[5], name=f'buscar_atendimentos_{name_prefix}_modal'),
        path(f'{prefix}/relatorio_cpf_popup/', views[6], name=f'relatorio_por_cpf_{name_prefix}_popup'),
        path(f'{prefix}/gerar_relatorio_por_cpf/', views[7], name=f'gerar_relatorio_{name_prefix}_por_cpf'),
        path(f'{prefix}/relatorio_atendimento/<int:grupo_id>/', views[8], name=f'relatorio_atendimento_{name_prefix}'),
    ]


urlpatterns = [
    # Conselho Tutelar
    path('conselho_tutelar/', conselho_tutelar, name='conselho_tutelar'),

    # CREAS
    *_rotas_instituicao('creas', [
        creas, cadastro_atendimento_creas_form, cadastro_atendimento_creas_submit,
        mostra_todos_atendimentos_creas, edita_atendimento_creas,
        buscar_atendimentos_creas_modal, relatorio_por_cpf_creas_popup,
        gerar_relatorio_creas_por_cpf, gerar_relatorio_atendimento_creas,
    ], 'creas'),

    # CRAS
    *_rotas_instituicao('cras', [
        cras, cadastro_atendimento_cras_form, cadastro_atendimento_cras_submit,
        mostra_todos_atendimentos_cras, edita_atendimento_cras,
        buscar_atendimentos_cras_modal, relatorio_por_cpf_cras_popup,
        gerar_relatorio_cras_por_cpf, gerar_relatorio_atendimento_cras,
    ], 'cras'),

    # CAPS
    *_rotas_instituicao('caps', [
        caps, cadastro_atendimento_caps_form, cadastro_atendimento_caps_submit,
        mostra_todos_atendimentos_caps, edita_atendimento_caps,
        buscar_atendimentos_caps_modal, relatorio_por_cpf_caps_popup,
        gerar_relatorio_caps_por_cpf, gerar_relatorio_atendimento_caps,
    ], 'caps'),

    # Secretaria da Saúde
    *_rotas_instituicao('secretaria_saude', [
        secretaria_saude, cadastro_atendimento_ss_form, cadastro_atendimento_ss_submit,
        mostra_todos_atendimentos_ss, edita_atendimento_ss,
        buscar_atendimentos_ss_modal, relatorio_por_cpf_ss_popup,
        gerar_relatorio_ss_por_cpf, gerar_relatorio_atendimento_ss,
    ], 'secretaria_saude'),
]