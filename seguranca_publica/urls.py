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
)
from .views.militar import militar
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

    path('militar/', militar, name='militar'),
    path('civil/', civil, name='civil'),
    path('cientifica/', cientifica, name='cientifica')
]
