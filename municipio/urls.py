# municipio/urls.py
from django.urls import path
from .view.conselho_tutelar import conselho_tutelar
from .view.cras import cras
from .view.caps import caps
from .view.secretaria_saude import secretaria_saude
from .view.creas import (
    creas,
    cadastro_atendimento_creas_form,
    cadastro_atendimento_creas_submit,
    mostra_todos_atendimentos_creas,
    edita_atendimento_creas,
    buscar_atendimentos_creas_modal,
    relatorio_por_cpf_creas_popup,
    gerar_relatorio_creas_por_cpf,
    gerar_relatorio_atendimento_creas,
)

app_name = 'municipio'

urlpatterns = [
    # Conselho Tutelar
    path('conselho_tutelar/', conselho_tutelar, name='conselho_tutelar'),

    # CREAS
    path('creas/', creas, name='creas'),
    path('creas/cadastro_atendimento_form/', cadastro_atendimento_creas_form, name='cadastro_atendimento_creas_form'),
    path('creas/cadastro_atendimento_submit/', cadastro_atendimento_creas_submit, name='cadastro_atendimento_creas_submit'),
    path('creas/todos_atendimentos/', mostra_todos_atendimentos_creas, name='mostra_todos_atendimentos_creas'),
    path('creas/edita_atendimento/<int:grupo_id>/', edita_atendimento_creas, name='edita_atendimento_creas'),
    path('creas/buscar_cpf_modal/', buscar_atendimentos_creas_modal, name='buscar_atendimentos_creas_modal'),
    path('creas/relatorio_cpf_popup/', relatorio_por_cpf_creas_popup, name='relatorio_por_cpf_creas_popup'),
    path('creas/gerar_relatorio_por_cpf/', gerar_relatorio_creas_por_cpf, name='gerar_relatorio_creas_por_cpf'),
    path('creas/relatorio_atendimento/<int:grupo_id>/', gerar_relatorio_atendimento_creas, name='relatorio_atendimento_creas'),

    # CRAS
    path('cras/', cras, name='cras'),

    # CAPS
    path('caps/', caps, name='caps'),

    # Secretaria da Saúde
    path('secretaria_saude/', secretaria_saude, name='secretaria_saude'),
]