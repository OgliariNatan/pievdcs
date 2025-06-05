from django.db import models
from seguranca_publica.models import *
from django import forms
from smart_selects.db_fields import ChainedForeignKey

from django.contrib.auth.models import User
from django.utils import timezone

status_MP_choices = [
    ("SO", "Solicitada"),
    ('NO', 'Não Solicitada'),
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
    ("AN", "Não Alfabetizado"),
    ("FI", "Ensino Fundamental Incompleto"),
    ("FC", "Ensino Fundamental Completo"),
    ("EI", "Ensino Médio Incompleto"),
    ("EC", "Ensino Médio Completo"),
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
        #help_text="Estado ao qual o município pertence"
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
        verbose_name="Nome do Pai*",
        null=False, blank=False,
        #help_text="Nome completo do pai da vítima",
    )
    nome_da_mae = models.CharField(
        max_length=250,
        verbose_name="Nome da Mãe*",
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
        #help_text="Escolha a nacionalidade da vítima",
    )  
    
    estado = models.CharField(
        max_length=2,
        choices=estado_choices,
        default="SC",
        null=False, blank=False,
        verbose_name="Estado*",
        #help_text="Escolha o estado de nascimento da vítima",
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
        #help_text="Informe o município de nascimento da vítima",
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
    endereco_numero = models.CharField(
        max_length=20, 
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
    agressor = models.ForeignKey(
        'Agressor_dados',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name="Agressor*",
        #help_text="Selecione o agressor cadastrado. Caso não exista, cadastre primeiro em 'Dados do Agressor'.",
        related_name="vitimas"
    )
    numero_AUTOS = models.CharField(
        verbose_name="Nº Autos",
        max_length=50,  
        null=True, blank=True,
        #help_text="Número do auto de prisão em flagrante",
    )

    status_MP = models.CharField(
        max_length=2,
        choices=status_MP_choices,
        verbose_name="Status da Medida Protetiva",
        default="SO",
        null=True, blank=True,
        #help_text="Status da medida protetiva",
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
        verbose_name="Nome Completo*", 
        null=False, blank=False,
        #related_name="agressor_ID",
        #help_text="Nome completo do agressor",
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
        verbose_name="Nome do Pai*",
        null=True, blank=False,
        #help_text="Nome completo do pai da vítima",
    )
    nome_da_mae = models.CharField(
        max_length=250,
        verbose_name="Nome da Mãe*",
        null=True, blank=False,
        #help_text="Nome completo da mãe da vítima",
    )
    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento*", 
        unique=False, null=False, blank=False,
        help_text="DD/MM/AAAA",
    )
    sexo = models.CharField(
        max_length=1,
        choices=sexo_choices,
        verbose_name="Sexo*",
        default="M",
        null=False, blank=False,
        #help_text="Escolha o sexo do agressor",
    )
    idade = models.PositiveIntegerField(null=True, blank=True, editable=False)
    nacionalidade = models.CharField(
        max_length=2, 
        verbose_name="Nacionalidade*", 
        choices=nacionalidade_choices, 
        default="BR",
        null=False, blank=False,
        #help_text="Escolha a nacionalidade do agressor",
    )  
    estado = models.CharField(
        max_length=2, 
        verbose_name="Estado*", 
        choices=estado_choices, 
        default="SC",
        null=False, blank=False,
        #help_text="Escolha o estado de nascimento do agressor",
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
        #help_text="Informe o município de nascimento da vítima",
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
    telefone = models.CharField(
        max_length=15, 
        verbose_name="Telefone*", 
        #help_text="(DD) XXXXX-XXXX",
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
        verbose_name="Nome do Pai*",
        #help_text="Selecione o pai do filho",
    )

    nome_mae = models.ForeignKey(
        Vitima_dados,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Nome da Mãe*",
        #help_text="Selecione a mãe do filho",
    )
    estado = models.CharField(
        max_length=2,
        verbose_name="Estado*",
        choices=estado_choices,
        default="SC",
        null=False, blank=False,
        #help_text="Escolha o estado de nascimento do filho",
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