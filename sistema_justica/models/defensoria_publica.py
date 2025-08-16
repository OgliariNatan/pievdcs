from django.db import models
from datetime import datetime, timedelta, timezone
from usuarios.models import CustomUser
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado
from seguranca_publica.models.base import grau_parentesco_agressor_choices, status_MP_choices, tipo_de_violencia_choices
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField, GroupedForeignKey
from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario


def default_periodo_mp():
    '''
    Função para definir o período padrão da medida protetiva
    que será de 120 dias a partir da data atual
    '''
    return datetime.now().date()  + timedelta(days=120)



class FormularioMedidaProtetiva(models.Model):
    '''
    Formulario para preencimento da Defensoria Pública
    solicitando a Medida Protetiva
    '''
    ID = models.AutoField(
        primary_key=True,
        #auto_created=True,
    )

    data_solicitacao = models.DateTimeField(
        default=datetime.now, 
        verbose_name='Data de Solicitação'
    )
        
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

    periodo_mp = models.DateField(
        default=default_periodo_mp,
        verbose_name='Período da Medida Protetiva'
    )

    solicitada_mpu = models.BooleanField(
        default=True,
        verbose_name='Medida Protetiva de Urgência'
    )
    
    tipo_de_violencia = models.CharField(
        max_length= 50, 
        choices= tipo_de_violencia_choices, 
        verbose_name= "Tipo de Violência",
    )

    comarca_competente = models.ForeignKey(
        ComarcasPoderJudiciario,
        on_delete=models.CASCADE,
        verbose_name='Comarca Competente',
        null=True, 
        blank=True
    )
    municipio_mp = ChainedForeignKey(
        Municipio,
        chained_field="comarca_competente",
        chained_model_field="comarcas_abrangentes",
        show_all=False,  # Altere para True para garantir que todos os municípios sejam exibidos
        auto_choose=True, 
        sort=True,
        verbose_name="Município do Fato",
        null=True,
        blank=True,  # Permita campo em branco para evitar erro de validação
        #help_text="Selecione apenas os municípios elegíveis para a comarca selecionada."
    )
    
    bairro_mp = models.CharField(
        max_length=100,
        verbose_name='Bairro:',
        null=True, 
        blank=False
    )

    grau_parentesco_agressor = models.CharField(
        max_length=15,
        choices=grau_parentesco_agressor_choices,
        default='Conjuge',
        verbose_name="Grau de Parentesco com o Agressor"
    )

    filhos = ChainedManyToManyField(
        Filhos_dados,
        chained_field="agressor",
        chained_model_field="agressor",
        verbose_name='Filhos',
        blank=True,
        null=True
    )
    class Meta:
        verbose_name = 'Formulario MP'
        verbose_name_plural = 'Formularios MP'
        ordering = ['data_solicitacao']
    def __str__(self):
        return f'Solicitação: {self.vitima} - ID: {self.ID}'