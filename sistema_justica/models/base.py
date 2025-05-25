from django.db import models
from seguranca_publica.models import *

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
    ("AN", "Analfabeto"),
    ("EF", "Ensino Fundamental"),
    ("EM", "Ensino Médio"),
    ("SU", "Superior Incompleto"),
    ("SS", "Superior Completo"),
    ("PO", "Pós-Graduação"),
]



class Vitima_dados(models.Model):
    """
    Modelo para armazenar os dados da vítima.
    """
    id = models.AutoField(primary_key=True)
    nome = models.CharField(
        max_length=250, 
        unique=True, 
        verbose_name="Nome Completo da Vítima", 
        null=True, blank=False,
        help_text="Nome completo da vítima",
    )
    cpf = models.CharField(
        max_length=14,  # 000.000.000-00
        unique=False,
        verbose_name="CPF da Vítima",
        null=True, blank=False,
        help_text="Formato: 000.000.000-00",
    )

    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento da Vítima", 
        unique=True, null=True, blank=False,
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
        null=True, blank=False,
        help_text="Escolha a nacionalidade da vítima",
    )  

    endereco = models.CharField(max_length=255, verbose_name="Endereço da Vítima")
    telefone = models.CharField(
        max_length=15, 
        verbose_name="Telefone da Vítima", 
        help_text="Formato: (DDD) XXXXX-XXXX",
    )
    email = models.EmailField(verbose_name="Email da Vítima", unique=True, null=True, blank=False)
    escolaridade = models.CharField(
        max_length=2, 
        choices=escolaridade_choices, 
        verbose_name="Escolaridade da Vítima", 
        default="EF",
        null=True, blank=False,
        help_text="Escolha a escolaridade da vítima",
    )
    nome_agressor = models.CharField(
        "agressor_dados.nome", 
        max_length=250, 
        null=True, blank=False,
        help_text="Nome do agressor, se conhecido. Caso contrário, deixe em branco.",
    )
    usuario = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, blank=True,
        verbose_name="Usuário",
        help_text="Usuário Responsável pelos dados da vítima",
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
        #auto_increment=True, 
        
    )
    nome = models.CharField(
        max_length=250, 
        unique=True, 
        verbose_name="Nome Completo do Agressor", 
        null=False, blank=False,
        #related_name="agressor_ID",
        help_text="Nome completo do agressor",
    )
    cpf = models.CharField(
        max_length=14,  # 000.000.000-00
        unique=False,
        verbose_name="CPF do Agressor",
        null=False, blank=False,
        help_text="Formato: 000.000.000-00",
    )

    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento do Agressor", 
        unique=True, null=False, blank=False,
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