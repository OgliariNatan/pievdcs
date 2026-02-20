# municipio/admin.py
# Registro dos modelos do município no Django Admin

from django.contrib import admin
from .models.creas import AtendimentoCREAS, TipoAtendimentoCREAS


@admin.register(AtendimentoCREAS)
class AtendimentoCREASAdmin(admin.ModelAdmin):
    """Admin para atendimentos do CREAS."""
    list_display = (
        'data_atendimento',
        'setor_atendimento',
        'atendimento',
        'usuario',
        'criado_em',
    )
    list_filter = ('setor_atendimento', 'data_atendimento')
    search_fields = (
        'agressores_atendidos__nome',
        'avaliacao',
    )
    filter_horizontal = ('agressores_atendidos',)
    readonly_fields = ('criado_em', 'atualizado_em', 'atualizado_por')
    ordering = ('-data_atendimento',)

    def get_queryset(self, request):
        """Retorna apenas atendimentos vinculados ao CREAS."""
        return super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        """Registra o usuário que criou/atualizou."""
        if change:
            obj.atualizado_por = request.user
        if not obj.usuario:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(TipoAtendimentoCREAS)
class TipoAtendimentoCREASAdmin(admin.ModelAdmin):
    """Admin para tipos de atendimento do CREAS."""
    list_display = ('instituicao_responsavel', 'tematica')
    list_filter = ('tematica',)

    def get_queryset(self, request):
        """Retorna apenas tipos de atendimento do CREAS."""
        return super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        """Força a instituição como CREAS ao salvar."""
        obj.instituicao_responsavel = 'CREAS'
        super().save_model(request, obj, form, change)