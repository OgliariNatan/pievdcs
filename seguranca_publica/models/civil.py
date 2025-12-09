
from django.db import models
from .base import OcorrenciaBase

class Investigacao(models.Model):
    delegado = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    def __str__(self):
        return f'{self.delegado} - {self.status}'
    class Meta:
        verbose_name = 'Investigação'
        verbose_name_plural = 'Investigações'

class OcorrenciaCivil(OcorrenciaBase):
    investigacao = models.OneToOneField(Investigacao, on_delete=models.CASCADE)
    flagrante = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Inserção Polícia Civil"
        verbose_name_plural = "Inserções da Policia Civil"

