from django.urls import path
from . import views

app_name = 'mensageria'

urlpatterns = [
    path('notificacoes/', views.listar_notificacoes, name='listar_notificacoes'),
    path('marcar-lida/<int:notificacao_id>/', views.marcar_como_lida, name='marcar_como_lida'),
    path('marcar-todas-lidas/', views.marcar_todas_lidas, name='marcar_todas_lidas'),
    path('contador-nao-lidas/', views.contador_nao_lidas, name='contador_nao_lidas'),
]