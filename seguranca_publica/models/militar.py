
from django.db import models
from .base import OcorrenciaBase
from seguranca_publica.models.base import Vitima_dados

class Patrulhamento(models.Model):
    local = models.CharField(max_length=255)
    horario = models.DateTimeField()
    equipe = models.CharField(max_length=255)

class OcorrenciaMilitar(OcorrenciaBase):
    tipo_patrulha = models.CharField(max_length=100)
    patrulhamento = models.ForeignKey(Patrulhamento, on_delete=models.SET_NULL, null=True)
