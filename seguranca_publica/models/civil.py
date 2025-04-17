
from django.db import models
from .base import OcorrenciaBase

class Investigacao(models.Model):
    delegado = models.CharField(max_length=100)
    status = models.CharField(max_length=50)

class OcorrenciaCivil(OcorrenciaBase):
    investigacao = models.OneToOneField(Investigacao, on_delete=models.CASCADE)
    flagrante = models.BooleanField(default=False)
