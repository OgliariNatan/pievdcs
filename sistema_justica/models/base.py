from django.db import models
from seguranca_publica.models import *
from django import forms
from smart_selects.db_fields import ChainedForeignKey

from django.contrib.auth.models import User
from django.utils import timezone

status_MP_choices = [
    ("SO", "Solicitada"),
    ("AP", "Aprovada"),
    ("RE", "Rejeitada"),
    ("CA", "Cancelada"),
    ("AT", "Ativa"),
    ("EV", "Em Vigor"),
]

sexo_choices = [
    ("M", "Masculino"),
    ("F", "Feminino"),
    ("O", "Outro"),
]

nacionalidade_choices = [
    ("BR", "Brasileiro"),
    ("PT", "Português"),
    ("ES", "Espanhol"),
    ("EN", "Inglês"),
    ("FR", "Francês"),
    ("IT", "Italiano"),
    ("DE", "Alemão"),
    ("CN", "Chinês"),
    ("JP", "Japonês"),
    ("IN", "Indiano"),
]

escolaridade_choices = [
    ("AN", "Analfabeto"),
    ("EF", "Ensino Fundamental"),
    ("EM", "Ensino Médio"),
    ("SU", "Superior Incompleto"),
    ("SS", "Superior Completo"),
    ("PO", "Pós-Graduação"),
]


estado_choices = [
    ("AC", "Acre"),
    ("AL", "Alagoas"),
    ("AP", "Amapá"),
    ("AM", "Amazonas"),
    ("BA", "Bahia"),
    ("CE", "Ceará"),
    ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"),
    ("GO", "Goiás"),
    ("MA", "Maranhão"),
    ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"),
    ("PA", "Pará"),
    ("PB", "Paraíba"),
    ("PR", "Paraná"),
    ("PE", "Pernambuco"),
    ("PI", "Piauí"),
    ("RJ", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"),
    ("RO", "Rondônia"),
    ("RR", "Roraima"),
    ("SC", "Santa Catarina"),
    ("SP", "São Paulo"),
    ("SE", "Sergipe"),
    ("TO", "Tocantins"),
    ("EX", "Estrangeiro"),
]



class Municipio(models.Model):
    """
    Modelo para armazenar os dados do município.
    """
    nome = models.CharField(max_length=100, verbose_name="Município")
    estado = models.CharField(
        max_length=2,
        choices=estado_choices,
        verbose_name="Estado",
        help_text="Estado ao qual o município pertence"
    )

    def __str__(self):
        return f"{self.nome} ({self.estado})"




class Vitima_dados(models.Model):
    """
    Modelo para armazenar os dados da vítima.
    """
    id = models.AutoField(primary_key=True)
    nome = models.CharField(
        max_length=250, 
        unique=False, 
        verbose_name="Nome Completo da Vítima", 
        null=True, blank=True,
        help_text="Nome completo da vítima",
    )
    cpf = models.CharField(
        max_length=14,  # 000.000.000-00
        unique=False,
        verbose_name="CPF da Vítima",
        null=False, blank=False,
        help_text="Formato: 000.000.000-00",
    )

    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento da Vítima", 
        unique=False, null=False, blank=False,
        help_text="Data de nascimento da vítima",
    )
    sexo = models.CharField(
        max_length=1,
        choices=sexo_choices,
        verbose_name="Sexo da Vítima",
        null=True, blank=False,
        help_text="Escolha o sexo da vítima",
    )
    idade = models.PositiveIntegerField(null=True, blank=True, editable=False)
    nacionalidade = models.CharField(
        max_length=2, 
        verbose_name="Nacionalidade da Vítima", 
        choices=nacionalidade_choices, 
        default="BR",
        null=True, blank=True,
        help_text="Escolha a nacionalidade da vítima",
    )  
    
    estado = models.CharField(
        max_length=2,
        choices=estado_choices,
        default="SC",
        null=True, blank=True,
        verbose_name="Estado da Vítima",
        help_text="Escolha o estado de nascimento da vítima",
    )
    municipio = ChainedForeignKey(
        Municipio,
        chained_field="estado",
        chained_model_field="estado",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=True,
        verbose_name="Município da Vítima",
        help_text="Informe o município de nascimento da vítima",
    )
    endereco_rua = models.CharField(max_length=255, verbose_name="Endereço da Vítima", null=True, blank=False)
    endereco_numero = models.CharField(
        max_length=20, 
        verbose_name="Número do Endereço da Vítima", 
        null=True, blank=False,
    )
    email = models.EmailField(verbose_name="Email da Vítima", unique=True, null=True, blank=True)
    escolaridade = models.CharField(
        max_length=2, 
        choices=escolaridade_choices, 
        verbose_name="Escolaridade da Vítima", 
        default="EF",
        null=True, blank=False,
        help_text="Escolha a escolaridade da vítima",
    )
    agressor = models.ForeignKey(
        'Agressor_dados',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Agressor",
        help_text="Selecione o agressor cadastrado. Caso não exista, cadastre primeiro em 'Dados do Agressor'.",
        related_name="vitimas"
    )
    numero_AUTOS = models.CharField(
        verbose_name="Número do Auto",
        max_length=50,  
        null=True, blank=False,
        help_text="Número do auto de prisão em flagrante",
    )

    status_MP = models.CharField(
        max_length=2,
        choices=status_MP_choices,
        verbose_name="Status da Medida Protetiva",
        default="SO",
        help_text="Status da medida protetiva",
    )



    def save(self, *args, **kwargs):
        # Calcula a idade antes de salvar
        today = timezone.now().date()
        if self.data_nascimento:
            self.idade = today.year - self.data_nascimento.year - (
                (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        else:
            self.idade = None

        # Remove qualquer caractere não numérico do CPF
        cpf_digits = ''.join(filter(str.isdigit, self.cpf))
        # Formata como 000.000.000-00 se o comprimento for 11
        if len(cpf_digits) == 11:
            self.cpf = f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"
        super().save(*args, **kwargs)


    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Dados da Vítima"
        verbose_name_plural = "Dados das Vítimas"
       
class Agressor_dados(models.Model):
    """
    Modelo para armazenar os dados do agressor.
    """
    id = models.AutoField(
        primary_key=True,
        verbose_name="ID do Agressor",
    )
    nome = models.CharField(
        max_length=250, 
        unique=False, 
        verbose_name="Nome Completo do Agressor", 
        null=False, blank=False,
        #related_name="agressor_ID",
        help_text="Nome completo do agressor",
    )
    cpf = models.CharField(
        max_length=14,  # 000.000.000-00
        unique=True,
        verbose_name="CPF do Agressor",
        null=False, blank=False,
        help_text="Formato: 000.000.000-00",
    )

    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento do Agressor", 
        unique=False, null=False, blank=False,
        help_text="DD/MM/AAAA",
    )
    sexo = models.CharField(
        max_length=1,
        choices=sexo_choices,
        verbose_name="Sexo do Agressor",
        null=False, blank=False,
        help_text="Escolha o sexo do agressor",
    )
    idade = models.PositiveIntegerField(null=True, blank=True, editable=False)
    nacionalidade = models.CharField(
        max_length=2, 
        verbose_name="Nacionalidade do Agressor", 
        choices=nacionalidade_choices, 
        default="BR",
        null=False, blank=False,
        help_text="Escolha a nacionalidade do agressor",
    )  
    estado = models.CharField(
        max_length=2, 
        verbose_name="Estado do Agressor", 
        choices=estado_choices, 
        default="SC",
        null=False, blank=False,
        help_text="Escolha o estado de nascimento do agressor",
    )
    endereco = models.CharField(max_length=255, verbose_name="Endereço do Agressor")
    telefone = models.CharField(
        max_length=15, 
        verbose_name="Telefone do Agressor", 
        help_text="Formato: (DDD) XXXXX-XXXX",
    )
    email = models.EmailField(verbose_name="Email do Agressor", unique=True, null=False, blank=False)
    escolaridade = models.CharField(
        max_length=2, 
        choices=escolaridade_choices, 
        verbose_name="Escolaridade do Agressor", 
        default="EF",
        null=False, blank=False,
        help_text="Escolha a escolaridade do agressor",
    )

    def save(self, *args, **kwargs):
        # Calcula a idade antes de salvar
        today = timezone.now().date()
        if self.data_nascimento:
            self.idade = today.year - self.data_nascimento

    class Meta:
        verbose_name = "Dados do Agressor"
        verbose_name_plural = "Dados dos Agressores"



class Filhos_dados(models.Model):
    """
    Modelo para armazenar os dados dos filhos.
    """
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=250, verbose_name="Nome Completo do Filho", null=True, blank=False)
    data_nascimento = models.DateField(verbose_name="Data de Nascimento do Filho", null=True, blank=False)
    sexo = models.CharField(max_length=1, choices=sexo_choices, verbose_name="Sexo do Filho", null=True, blank=False)
    idade = models.PositiveIntegerField(null=True, blank=True, editable=False)
    cpf = models.CharField(
        max_length=14,  # 000.000.000-00
        unique=False,
        verbose_name="CPF do Filho",
        null=True, blank=False,
        #default="000.000.000-00",
        help_text="Formato: 000.000.000-00",
    )
    nacionalidade = models.CharField(
        max_length=2, 
        verbose_name="Nacionalidade do Filho", 
        choices=nacionalidade_choices, 
        default="BR",
        null=False, blank=False,
        help_text="Escolha a nacionalidade do filho",
    )
    nome_pai = models.ForeignKey(
        Agressor_dados,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Nome do Pai",
        help_text="Selecione o pai do filho",
    )

    nome_mae = models.ForeignKey(
        Vitima_dados,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Nome da Mãe",
        help_text="Selecione a mãe do filho",
    )
    estado = models.CharField(
        max_length=2, 
        verbose_name="Estado do Filho", 
        choices=estado_choices, 
        default="SC",
        null=False, blank=False,
        help_text="Escolha o estado de nascimento do filho",
    )

    def save(self, *args, **kwargs):
        # Calcula a idade antes de salvar
        today = timezone.now().date()
        if self.data_nascimento:
            self.idade = today.year - self.data_nascimento.year - (
                (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        else:
            self.idade = None

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Dados dos Filhos"
        verbose_name_plural = "Dados dos Filhos"