# Registro de models aqui
from django.contrib import admin
from .models.militar import OcorrenciaMilitar, Patrulhamento
from .models.civil import OcorrenciaCivil, Investigacao
from .models.base import OcorrenciaBase

class OcorrenciaMilitarAdmin(admin.ModelAdmin):
    pass

    #list_display = all
    




admin.site.register(OcorrenciaMilitar, OcorrenciaMilitarAdmin)
admin.site.register(Patrulhamento)
admin.site.register(OcorrenciaCivil)
admin.site.register(Investigacao)
