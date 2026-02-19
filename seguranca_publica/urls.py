from django.urls import path
from .views.penal import (
    penal, 
    cadastro_tipo_atendimento_form, 
    cadastro_tipo_atendimento_submit, 
    cadastro_atendimento_penal_form, 
    cadastro_atendimento_penal_submit, 
    buscar_atendimentos_por_cpf_ajax, 
    buscar_atendimentos_por_cpf_modal,
    mostra_todos_grupos_penal,
    edita_atendimento_pp, gerar_relatorio_atendimento,
    relatorio_por_cpf_popup, gerar_relatorio_por_cpf,
)
from .views.militar import (
    militar,
    consultas_informacao_vitima_agressor,
    buscar_vitimas,
    detalhe_medida_protetiva, historico_mp_vitima, historico_mp_agressor
)
from .views.civil import civil
from .views.cientifica import cientifica

app_name = 'seguranca_publica'

urlpatterns = [
    #Instituição Penal
    path('penal/', penal, name='penal'),
    path('cadastro_tipo_atendimento_form/', cadastro_tipo_atendimento_form, name='cadastro_tipo_atendimento_form'),
    path('cadastro_tipo_atendimento_submit/', cadastro_tipo_atendimento_submit, name='cadastro_tipo_atendimento_submit'),
    path('cadastro_atendimento_penal_form/', cadastro_atendimento_penal_form, name='cadastro_atendimento_penal_form'),
    path('cadastro_atendimento_penal_submit/', cadastro_atendimento_penal_submit, name='cadastro_atendimento_penal_submit'),
    path('buscar-atendimentos-ajax/', buscar_atendimentos_por_cpf_ajax, name='buscar_atendimentos_por_cpf_ajax'),
    path('buscar-atendimentos-modal/', buscar_atendimentos_por_cpf_modal, name='buscar_atendimentos_por_cpf_modal'),
    path('mostra_todos_grupos_penal/', mostra_todos_grupos_penal, name='mostra_todos_grupos_penal'),
    path('edita_atendimento_pp/<int:grupo_id>/', edita_atendimento_pp, name='edita_atendimento_pp'),
    path('relatorio_atendimento/<int:grupo_id>/', gerar_relatorio_atendimento, name='relatorio_atendimento'),
    path('relatorio_por_cpf_popup/', relatorio_por_cpf_popup, name='relatorio_por_cpf_popup'),
    path('gerar_relatorio_por_cpf/', gerar_relatorio_por_cpf, name='gerar_relatorio_por_cpf'),


    #Instituição Militar
    path('militar/', militar, name='militar'),
    path('consultas_PM/', consultas_informacao_vitima_agressor, name='consultas_PM'),
    path('buscar_vitimas/', buscar_vitimas, name='buscar_vitimas'),
    path('detalhe_medida_protetiva/<int:medida_id>/', detalhe_medida_protetiva, name='detalhe_medida_protetiva'),
    path('historico_mp_vitima/<str:cpf_vitima>/', historico_mp_vitima, name='historico_mp_vitima'),
    path('historico_mp_agressor/<str:cpf_agressor>/', historico_mp_agressor, name='historico_mp_agressor'),
    
    path('civil/', civil, name='civil'),
    path('cientifica/', cientifica, name='cientifica')
]
