# Registro de models aqui
from django.contrib import admin
from .models.militar import OcorrenciaMilitar, Patrulhamento
from .models.civil import OcorrenciaCivil, Investigacao
from .models.base import OcorrenciaBase

class OcorrenciaMilitarAdmin(admin.ModelAdmin):
    list_display = (
        'numero_ocorrencia',
        'data',
        'tipo_patrulha',
        'equipe',  # agora usa o property
        'vtr',
    )



admin.site.register(OcorrenciaMilitar, OcorrenciaMilitarAdmin)
admin.site.register(Patrulhamento)
admin.site.register(OcorrenciaCivil)
admin.site.register(Investigacao)
