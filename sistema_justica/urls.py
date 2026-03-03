from django.urls import path
from .views.poder_judiciario import( 
    poder_judiciario, cadastro_vitima_form, cadastro_vitima_submit,
    cadastro_agressor_form, cadastro_agressor_submit,
    cadastro_municipio_form, cadastro_municipio_submit, chat_ia,
    listar_medidas_protetivas, form_alterar_periodo_mp,
    alterar_periodo_mp, detalhe_medida_protetiva_jud, listar_grupos_reflexivos
)
from .views.ministerio_publico import ministerio_publico
from .views.defensoria_publica import(
    defensoria_publica, cadastro_mpu, listar_encaminhamentos,
    consultar_mp, editar_mpu,
)
from sistema_justica.forms.cadastros import CadastroVitimaForm, CadastroAgressorForm, CadastroMunicipioForm

app_name = 'sistema_justica'

urlpatterns = [

    path('poder_judiciario/', poder_judiciario, name='poder_judiciario'), #Relacionado ao judiciario
    path('medidas_protetivas/', listar_medidas_protetivas, name='listar_medidas_protetivas'),
    path('medida_protetiva/<int:medida_id>/alterar_periodo/', form_alterar_periodo_mp, name='form_alterar_periodo_mp'),
    path('medida_protetiva/<int:medida_id>/alterar_periodo/submit/', alterar_periodo_mp, name='alterar_periodo_mp'),
    path('medida_protetiva/<int:medida_id>/detalhe/', detalhe_medida_protetiva_jud, name='detalhe_medida_protetiva_jud'),
    path('grupos_reflexivos/', listar_grupos_reflexivos, name='listar_grupos_reflexivos'),


    path('ministerio_publico/', ministerio_publico, name='ministerio_publico'), #Relacionado ao ministerio publico
    path('defensoria_publica/', defensoria_publica, name='defensoria_publica'), #Relacionado ao defensoria publica 

    path('cadastro_vitima_form/', cadastro_vitima_form, name='cadastro_vitima_form'), #Formulário de cadastro de vitima
    path('cadastro_vitima_submit/', cadastro_vitima_submit, name='cadastro_vitima_submit'), #Submissão do formulário de cadastro de vitima
    path('cadastro_agressor_form/', cadastro_agressor_form, name='cadastro_agressor_form'), #Formulário de cadastro de agressor
    path('cadastro_agressor_submit/', cadastro_agressor_submit, name='cadastro_agressor_submit'), #Submissão do formulário de cadastro de agressor
    path('cadastro_municipio_form/', cadastro_municipio_form, name='cadastro_municipio_form'),
    path('cadastro_municipio_submit/', cadastro_municipio_submit, name='cadastro_municipio_submit'),
    path('chat_ia/', chat_ia, name='chat_ia'),
    path("encaminhamentos/", listar_encaminhamentos, name="encaminhamentos"), #Listar encaminhamentos da defensoria pública


    path('cadastro_mpu/', cadastro_mpu, name='cadastro_mpu'), #Cadastro MPU
    path('consultar_mp/', consultar_mp, name='consultar_mp'), #Consulta de MPUs para Defensoria Pública e Ministério Público
    path('editar_mpu/<int:mpu_id>/', editar_mpu, name='editar_mpu'), #Editar MPU
]