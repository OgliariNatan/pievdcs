from django.urls import path
from .views.poder_judiciario import poder_judiciario, cadastro_vitima_form, cadastro_vitima_submit, cadastro_agressor_form, cadastro_agressor_submit
from .views.ministerio_publico import ministerio_publico
from .views.defensoria_publica import defensoria_publica


app_name = 'sistema_justica'

urlpatterns = [

    path('poder_judiciario/', poder_judiciario, name='poder_judiciario'), #Relacionado ao judiciario    
    path('ministerio_publico/', ministerio_publico, name='ministerio_publico'), #Relacionado ao ministerio publico
    path('defensoria_publica/', defensoria_publica, name='defensoria_publica'), #Relacionado ao defensoria publica 

    path('cadastro_vitima_form/', cadastro_vitima_form, name='cadastro_vitima_form'), #Formulário de cadastro de vitima
    path('cadastro_vitima_submit/', cadastro_vitima_submit, name='cadastro_vitima_submit'), #Submissão do formulário de cadastro de vitima
    path('cadastro_agressor_form/', cadastro_agressor_form, name='cadastro_agressor_form'), #Formulário de cadastro de agressor
    path('cadastro_agressor_submit/', cadastro_agressor_submit, name='cadastro_agressor_submit'), #Submissão do formulário de cadastro de agressor
    
]