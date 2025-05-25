
from django.db import models
from sistema_justica.models.base import Vitima_dados



class OcorrenciaBase(models.Model):
    numero_ocorrencia = models.CharField(max_length=50)
    data = models.DateTimeField()
    vitima = models.ForeignKey(Vitima_dados, on_delete=models.CASCADE,)
    descricao = models.TextField(verbose_name="Descrição da Ocorrência")

    class Meta:
        abstract = True
