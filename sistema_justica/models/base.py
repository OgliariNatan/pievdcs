from django.db import models
from datetime import date
from seguranca_publica.models import *
from django import forms
from smart_selects.db_fields import ChainedForeignKey

from django.contrib.auth.models import User
from django.utils import timezone


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
    ("AN", "Não Alfabetizado"),
    ("FI", "Ensino Fundamental Incompleto"),
    ("FC", "Ensino Fundamental Completo"),
    ("EI", "Ensino Médio Incompleto"),
    ("EC", "Ensino Médio Completo"),
    ("SU", "Superior Incompleto"),
    ("SS", "Superior Completo"),
    ("PO", "Pós-Graduação"),
]

etnia_choices = [
    ("BR", "Branca"),
    ("PR", "Preta"),
    ("PA", "Parda"),
    ("AM", "Amarela"),
    ("IN", "Indígena"),
]


classeEconomica_choices = [
    ("SR", "Sem Renda"),
    ("AB", "Abaixo de R$1.518,00"),
    ("BA", "De R$1.518,01 a R$3.636,00"),
    ("BC", "De R$3.636,01 a R$7.017,63"),
    ("BD", "De R$7.017,64 a R$28.239,99"),
    ("AC", "Acima de R$28.240,00"),
]

class Estado(models.Model):
    """
    Modelo para armazenar os estados brasileiros.
    """
    sigla = models.CharField(
        max_length= 2,
        verbose_name="Sigla do Estado",
        unique=True,
        null=True, blank=False,
    )
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome do Estado",
        null=True, blank=False,
    )
    def __str__(self):
        return f'{self.sigla}'


class Municipio(models.Model):
    """
    Modelo para armazenar os dados do município.
    """
    nome = models.CharField(
        max_length=100, 
        verbose_name="Município"
    )
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        null=True, blank=False,
        verbose_name="Estado"
    )

    def __str__(self):
        return f"{self.nome} ({self.estado})"




class Vitima_dados(models.Model):
    """
    Modelo para armazenar os dados da vítima.
    """
    id = models.AutoField(
        primary_key=True,
        verbose_name="ID da Vítima",
    )
    
    nome = models.CharField(
        max_length=250, 
        unique=False, 
        verbose_name="Nome Completo*", 
        null=False, blank=False,
        #help_text="Nome completo da vítima",
    )
    cpf = models.CharField(
        max_length=14,  # 000.000.000-00
        unique=False,
        verbose_name="CPF*",
        null=False, blank=False,
        help_text="000.000.000-00",
    )
    nome_social = models.CharField(
        max_length=250,
        verbose_name="Nome Social",
        null=True, blank=True,
        #help_text="Nome social da vítima",
    )
    nome_do_pai = models.CharField(
        max_length=250,
        verbose_name="Pai*",
        null=False, blank=False,
        #help_text="Nome completo do pai da vítima",
    )
    nome_da_mae = models.CharField(
        max_length=250,
        verbose_name="Mãe*",
        null=False, blank=False,
        #help_text="Nome completo da mãe da vítima",
    )
    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento*", 
        unique=False, null=False, blank=False,
        #help_text="Data de nascimento da vítima",
    )
    sexo = models.CharField(
        max_length=1,
        choices=sexo_choices,
        verbose_name="Sexo*",
        default="F",
        null=False, blank=False,
        #help_text="Escolha o sexo da vítima",
    )
    etnia = models.CharField(
        max_length=2,
        choices=etnia_choices,
        verbose_name="Etnia*",
        null=False, blank=False,
    )
    estado_civil = models.CharField(
        max_length=2,
        choices=[
            ("S", "Solteiro(a)"),
            ("C", "Casado(a)"),
            ("D", "Divorciado(a)"),
            ("V", "Viúvo(a)"),
            ("A", "Amasiado(a)"),
            ("U", "União Estável"),
            ("O", "Outros"),
        ],
        verbose_name="Estado Civil*",
    )

    idade = models.PositiveIntegerField(null=True, blank=True, editable=False)
    telefone = models.CharField(
        max_length=15,
        verbose_name="Telefone*",
        null=False, blank=False,
    )
    nacionalidade = models.CharField(
        max_length=2, 
        verbose_name="Nacionalidade*", 
        choices=nacionalidade_choices, 
        default="BR",
        null=False, blank=False,
    )  
    
    estado = models.ForeignKey(
        Estado,
        on_delete=models.SET_NULL,
        null=True, blank=False,
        verbose_name="Estado*",
    )
    municipio = ChainedForeignKey(
        Municipio,
        chained_field="estado",
        chained_model_field="estado",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True, blank=False,
        verbose_name="Município*",
    )
    bairro = models.CharField(
        max_length=100,
        verbose_name="Bairro*",
        null=False, blank=False,
    )
    endereco_rua = models.CharField(
        max_length=255, 
        verbose_name="Endereço*", 
        null=True, blank=False,
        #help_text="Informe o endereço residencial da vítima",
    )
    endereco_numero = models.IntegerField(
        verbose_name="Nº*",
        null=True, blank=True,
    )
    email = models.EmailField(
        verbose_name="Email",
        max_length=100, 
        unique=True, null=True, blank=True
    )
    escolaridade = models.CharField(
        max_length=2, 
        choices=escolaridade_choices, 
        verbose_name="Escolaridade*", 
        default="EF",
        null=False, blank=False,
        #help_text="Escolha a escolaridade da vítima",
    )
    classeEconomica = models.CharField(
        max_length=2,
        choices=classeEconomica_choices,
        verbose_name="Classe Econômica*",
        null=False, blank=False,
    )
    profissao = models.CharField(
        max_length=100,
        verbose_name="Profissão*",
        null=False, blank=False,
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

        # Remove qualquer caractere não numérico do CPF
        cpf_digits = ''.join(filter(str.isdigit, self.cpf))
        # Formata como 000.000.000-00 se o comprimento for 11
        if len(cpf_digits) == 11:
            self.cpf = f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.nome} ({self.cpf})"

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
        verbose_name="Nome*", 
        null=False, blank=False,
    )
    
    cpf = models.CharField(
        max_length=14,  # 000.000.000-00
        unique=True,
        verbose_name="CPF*",
        null=False, blank=False,
        help_text="000.000.000-00",
    )
    nome_social = models.CharField(
        max_length=250,
        verbose_name="Nome Social",
        null=True, blank=True,
        #help_text="Nome social da vítima",
    )
    nome_do_pai = models.CharField(
        max_length=250,
        verbose_name="Pai*",
        null=True, blank=False,
    )
    nome_da_mae = models.CharField(
        max_length=250,
        verbose_name="Mãe*",
        null=True, blank=False, unique=False,
    )
    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento*", 
        unique=False, null=True, blank=False,
    )
    
    sexo = models.CharField(
        max_length=1,
        choices=sexo_choices,
        verbose_name="Sexo*",
        default="M",
        null=False, blank=False,
    )
    etnia = models.CharField(
        max_length=2,
        choices=etnia_choices,
        verbose_name="Etnia*",
        null=False, blank=False,
    )
    estado_civil = models.CharField(
        max_length=2,
        choices=[
            ("S", "Solteiro(a)"),
            ("C", "Casado(a)"),
            ("D", "Divorciado(a)"),
            ("V", "Viúvo(a)"),
            ("A", "Amasiado(a)"),
            ("U", "União Estável"),
            ("O", "Outros"),
        ],
        verbose_name="Estado Civil*",
    )
    idade = models.PositiveIntegerField(
        null=True, blank=True, 
        editable=False,
    )
    telefone = models.CharField(
        max_length=15, 
        verbose_name="Telefone*",
    )
    nacionalidade = models.CharField(
        max_length=2, 
        verbose_name="Nacionalidade*", 
        choices=nacionalidade_choices, 
        default="BR",
        null=False, blank=False,
        #help_text="Escolha a nacionalidade do agressor",
    )  
    estado = models.ForeignKey(
        Estado,
        on_delete=models.SET_NULL,
        null=True, blank=False,
        verbose_name="Estado*",
    )
    municipio = ChainedForeignKey(
        Municipio,
        chained_field="estado",
        chained_model_field="estado",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True, blank=False,
        verbose_name="Município*",
    )
    bairro = models.CharField(
        max_length=100,
        verbose_name="Bairro*",
        null=True, blank=False,
    )

    endereco = models.CharField(
        max_length=255, 
        verbose_name="Endereço*",
        null=True, blank=False,
    )
    
    endereco_numero = models.IntegerField(
        verbose_name="Nº*",
        null=True, blank=False,
    )
    
    email = models.EmailField(verbose_name="Email", unique=True, null=True, blank=True)
    
    escolaridade = models.CharField(
        max_length=2, 
        choices=escolaridade_choices, 
        verbose_name="Escolaridade*", 
        default="EF",
        null=False, blank=False,
        #help_text="Escolha a escolaridade do agressor",
    )
    classeEconomica = models.CharField(
        max_length=2,
        choices=classeEconomica_choices,
        verbose_name="Renda Mensal*",
        null=False, blank=False,
    )
    profissao = models.CharField(
        max_length=100,
        verbose_name="Profissão*",
        null=False, blank=False,
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
        verbose_name = "Dados do Agressor"
        verbose_name_plural = "Dados dos Agressores"

    def __str__(self):
        return f"{self.nome} ({self.cpf})"


class Filhos_dados(models.Model):
    """
    Modelo para armazenar os dados dos filhos.
    """
    id = models.AutoField(
        primary_key=True,
        verbose_name="ID do Filho",
    )
    nome = models.CharField(
        max_length=250, 
        verbose_name="Nome Completo*", 
        null=True, blank=False
    )
    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento*", 
        null=True, blank=False
    )
    sexo = models.CharField(
        max_length=1,
        choices=sexo_choices,
        verbose_name="Sexo*",
        null=True, blank=False
    )
    idade = models.PositiveIntegerField(null=True, blank=True, editable=False)
    cpf = models.CharField(
        max_length=14,  # 000.000.000-00
        unique=False,
        verbose_name="CPF*",
        null=True, blank=True,
        #default="000.000.000-00",
        help_text="000.000.000-00",
    )
    nacionalidade = models.CharField(
        max_length=2, 
        verbose_name="Nacionalidade*", 
        choices=nacionalidade_choices, 
        default="BR",
        null=False, blank=False,
        #help_text="Escolha a nacionalidade do filho",
    )
    nome_pai = models.ForeignKey(
        Agressor_dados,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Pai*",
        #help_text="Selecione o pai do filho",
    )

    nome_mae = models.ForeignKey(
        Vitima_dados,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Mãe*",
        #help_text="Selecione a mãe do filho",
    )
    estado = models.ForeignKey(
        Estado,
        on_delete=models.SET_NULL,
        null=True, blank=False,
        verbose_name="Estado*",
    )
    municipio = ChainedForeignKey(
        Municipio,
        chained_field="estado",
        chained_model_field="estado",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=False,
        verbose_name="Município*",
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