from django.urls import path
from .views.penal import penal, cadastro_tipo_atendimento_form, cadastro_tipo_atendimento_submit, cadastro_atendimento_penal_form, cadastro_atendimento_penal_submit
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


    path('militar/', militar, name='militar'),
    path('civil/', civil, name='civil'),
    path('cientifica/', cientifica, name='cientifica')
]
