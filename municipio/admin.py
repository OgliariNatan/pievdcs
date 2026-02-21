# municipio/admin.py
# Registro dos modelos do município no Django Admin

from django.contrib import admin
from .models.creas import AtendimentoCREAS, TipoAtendimentoCREAS
from .models.cras import AtendimentoCRAS, TipoAtendimentoCRAS
from .models.caps import AtendimentoCAPS, TipoAtendimentoCAPS
from .models.secretaria_saude import AtendimentoSecSaude, TipoAtendimentoSecSaude


# ──────────────────────────────────────────────
# Classe base reutilizável para evitar repetição
# ──────────────────────────────────────────────

class BaseAtendimentoAdmin(admin.ModelAdmin):
    """Admin base para atendimentos de todas as instituições."""
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

    def save_model(self, request, obj, form, change):
        """Registra o usuário que criou/atualizou."""
        if change:
            obj.atualizado_por = request.user
        if not obj.usuario:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


class BaseTipoAtendimentoAdmin(admin.ModelAdmin):
    """Admin base para tipos de atendimento."""
    list_display = ('instituicao_responsavel', 'tematica')
    list_filter = ('tematica',)
    instituicao = None  # Deve ser definido nas subclasses

    def save_model(self, request, obj, form, change):
        """Força a instituição ao salvar."""
        if self.instituicao:
            obj.instituicao_responsavel = self.instituicao
        super().save_model(request, obj, form, change)


# ──────────────────────────────────────────────
# CREAS
# ──────────────────────────────────────────────

@admin.register(AtendimentoCREAS)
class AtendimentoCREASAdmin(BaseAtendimentoAdmin):
    """Admin para atendimentos do CREAS."""
    pass


@admin.register(TipoAtendimentoCREAS)
class TipoAtendimentoCREASAdmin(BaseTipoAtendimentoAdmin):
    """Admin para tipos de atendimento do CREAS."""
    instituicao = 'CREAS'


# ──────────────────────────────────────────────
# CRAS
# ──────────────────────────────────────────────

@admin.register(AtendimentoCRAS)
class AtendimentoCRASAdmin(BaseAtendimentoAdmin):
    """Admin para atendimentos do CRAS."""
    pass


@admin.register(TipoAtendimentoCRAS)
class TipoAtendimentoCRASAdmin(BaseTipoAtendimentoAdmin):
    """Admin para tipos de atendimento do CRAS."""
    instituicao = 'CRAS'


# ──────────────────────────────────────────────
# CAPS
# ──────────────────────────────────────────────

@admin.register(AtendimentoCAPS)
class AtendimentoCAPSAdmin(BaseAtendimentoAdmin):
    """Admin para atendimentos do CAPS."""
    pass


@admin.register(TipoAtendimentoCAPS)
class TipoAtendimentoCAPSAdmin(BaseTipoAtendimentoAdmin):
    """Admin para tipos de atendimento do CAPS."""
    instituicao = 'CAPS'


# ──────────────────────────────────────────────
# Secretaria da Saúde
# ──────────────────────────────────────────────

@admin.register(AtendimentoSecSaude)
class AtendimentoSecSaudeAdmin(BaseAtendimentoAdmin):
    """Admin para atendimentos da Secretaria da Saúde."""
    pass


@admin.register(TipoAtendimentoSecSaude)
class TipoAtendimentoSecSaudeAdmin(BaseTipoAtendimentoAdmin):
    """Admin para tipos de atendimento da Secretaria da Saúde."""
    instituicao = 'Secretaria da Saúde'