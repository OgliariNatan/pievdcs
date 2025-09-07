from django.contrib import admin
from .models import Notificacao, StatusNotificacaoUsuario

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'prioridade', 'remetente', 'data_criacao']
    list_filter = ['tipo', 'prioridade', 'data_criacao']
    search_fields = ['titulo', 'mensagem']
    date_hierarchy = 'data_criacao'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'mensagem', 'tipo', 'prioridade')
        }),
        ('Destinatários', {
            'fields': ('destinatario_usuario', 'destinatario_grupo')
        }),
        ('Metadados', {
            'fields': ('remetente', 'url_acao', 'objeto_relacionado_tipo', 'objeto_relacionado_id')
        }),
    )

@admin.register(StatusNotificacaoUsuario)
class StatusNotificacaoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['notificacao', 'usuario', 'status', 'data_leitura']
    list_filter = ['status', 'data_leitura']
    search_fields = ['usuario__username', 'notificacao__titulo']