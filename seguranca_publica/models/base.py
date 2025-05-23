
from django.db import models
from usuarios.models import Vitima



class OcorrenciaBase(models.Model):
    numero_ocorrencia = models.CharField(max_length=50)
    data = models.DateTimeField()
    vitima = models.ForeignKey("usuarios.Vitima", on_delete=models.CASCADE)
    descricao = models.TextField(verbose_name="Descrição da Ocorrência")

    class Meta:
        abstract = True
