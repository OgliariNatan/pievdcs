from django.urls import path
from . import views

app_name = 'mensageria'

urlpatterns = [
    path('notificacoes/', views.listar_notificacoes, name='listar_notificacoes'),
    path('marcar-lida/<int:notificacao_id>/', views.marcar_notificacao_lida, name='marcar_notificacao_lida'),
    path('arquivar/<int:notificacao_id>/', views.arquivar_notificacao, name='arquivar_notificacao'),
    path('marcar-todas-lidas/', views.marcar_todas_lidas, name='marcar_todas_lidas'),
    path('api/contador/', views.api_contador_notificacoes, name='api_contador_notificacoes'),
    path('api/recentes/', views.api_notificacoes_recentes, name='api_notificacoes_recentes'),
]