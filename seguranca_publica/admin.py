# Registro de models aqui
from django.contrib import admin
from .models.militar import OcorrenciaMilitar, Patrulhamento
from .models.civil import OcorrenciaCivil, Investigacao
from .models.base import OcorrenciaBase

admin.site.register(OcorrenciaMilitar)
admin.site.register(Patrulhamento)
admin.site.register(OcorrenciaCivil)
admin.site.register(Investigacao)
#admin.site.register(OcorrenciaBase)
