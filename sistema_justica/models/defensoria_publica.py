from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado
from seguranca_publica.models.base import grau_parentesco_agressor_choices, status_MP_choices, tipo_de_violencia_choices
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField, GroupedForeignKey

class FormularioMedidaProtetiva(models.Model):
    '''
    Formulario para preencimento da Defensoria Pública
    solicitando a Medida Protetiva
    '''
    vitima = models.ForeignKey(
        Vitima_dados,
        on_delete=models.CASCADE,
        verbose_name='Vitima',
        null=True, blank=True
    )

    agressor = models.ForeignKey(
        Agressor_dados,
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name='Agressor'
    )

    mpu = models.BooleanField(
        default=True,
        verbose_name='Medida Protetiva de Urgência'
    )
    
    tipo_de_violencia = models.CharField(
        max_length= 50, 
        choices= tipo_de_violencia_choices, 
        verbose_name= "Tipo de Violência",
    )
    grau_parentesco_agressor = models.CharField(
        max_length= 15,
        choices= grau_parentesco_agressor_choices,
        default='Conjuge',
    )

    class Meta:
        verbose_name = 'Formulario MP'
        verbose_name_plural = 'Formularios MP'
    def __str__(self):
        return f'Solicitação: {self.vitima}'