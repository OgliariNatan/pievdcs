from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from sistema_justica.models.base import Municipio, Estado
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField, GroupedForeignKey

class ComarcasPoderJudiciario(models.Model):
    """
    Modelo para representar as comarcas do Poder Judiciário.
    """
    nome = models.CharField(max_length=100, verbose_name='Nome da Comarca')
    estado = models.ForeignKey(
        'Estado', 
        on_delete=models.CASCADE, 
        verbose_name='Estado'
    )
    
    municipios_abrangentes = ChainedManyToManyField(
        Municipio,
        chained_field="estado",
        chained_model_field="estado",
        auto_choose=True,
        #sort=True,
        blank=True,
        #null=True,
        horizontal=True,
        verbose_name='Municípios Abrangentes',
    )
    

    class Meta:
        verbose_name = 'Comarca do Poder Judiciário'
        verbose_name_plural = 'Comarcas do Poder Judiciário'
        ordering = ['nome']

    def __str__(self):
        return self.nome