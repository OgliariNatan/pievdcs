from django.contrib import admin
from .models import Notificacao

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'prioridade', 'remetente', 'get_destinatario', 'status', 'data_criacao']
    list_filter = ['tipo', 'prioridade', 'status', 'importante', 'data_criacao']
    search_fields = ['titulo', 'mensagem', 'remetente__username', 'destinatario_usuario__username']
    date_hierarchy = 'data_criacao'
    readonly_fields = ['data_criacao', 'data_atualizacao', 'data_leitura', 'data_arquivamento']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'mensagem', 'tipo', 'prioridade', 'importante')
        }),
        ('Destinatários', {
            'fields': ('destinatario_usuario', 'destinatario_grupo'),
            'description': 'Escolha apenas um tipo de destinatário: usuário OU grupo'
        }),
        ('Status e Rastreamento', {
            'fields': ('status', 'usuarios_que_leram', 'usuarios_que_arquivaram')
        }),
        ('Metadados', {
            'fields': ('remetente', 'objeto_relacionado_tipo', 'objeto_relacionado_id', 'data_expiracao')
        }),
        ('Timestamps', {
            'fields': ('data_criacao', 'data_atualizacao', 'data_leitura', 'data_arquivamento'),
            'classes': ('collapse',)
        }),
    )
    
    def get_destinatario(self, obj):
        """Exibe o destinatário (usuário ou grupo)"""
        if obj.destinatario_usuario:
            return f"Usuário: {obj.destinatario_usuario.get_full_name() or obj.destinatario_usuario.username}"
        elif obj.destinatario_grupo:
            return f"Grupo: {obj.destinatario_grupo.name}"
        return "-"
    get_destinatario.short_description = 'Destinatário'
    
    def save_model(self, request, obj, form, change):
        """Preenche automaticamente o remetente com o usuário atual se não estiver preenchido"""
        if not obj.remetente:
            obj.remetente = request.user
        super().save_model(request, obj, form, change)