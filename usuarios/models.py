from django.contrib.auth.models import AbstractUser, Group as DjangoGroup
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    # Seus campos personalizados aqui
    cpf_validator = RegexValidator(
        regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
        message='CPF deve estar no formato: 000.000.000-00'
    )
    
    # Validador para telefone
    phone_validator = RegexValidator(
        regex=r'^\(\d{2}\) \d{4,5}-\d{4}$',
        message='Telefone deve estar no formato: (00) 00000-0000 ou (00) 0000-0000'
    )

    cpf = models.CharField(
        'CPF',
        max_length=14,
        unique=True,
        validators=[cpf_validator],
        help_text='Formato: 000.000.000-00',
        null=True,
        blank=True
    )
    
    telefone = models.CharField(
        'Telefone',
        max_length=15,
        validators=[phone_validator],
        help_text='Formato: (00) 00000-0000',
        null=True,
        blank=True
    )
    
    foto = models.ImageField(
        'Foto do Perfil',
        upload_to='usuarios/fotos/%Y/%m/',
        null=True,
        blank=True,
        help_text='Foto do usuário'
    )

    # departamento = models.CharField(
    #     'Departamento',
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     #help_text='Departamento do usuário'
    # )

    # Sobrescrever os relacionamentos para usar grupos personalizados
    groups = models.ManyToManyField(
        'CustomGroup',
        verbose_name='grupos',
        blank=True,
        help_text='Os grupos aos quais este usuário pertence.',
        related_name='user_set',
        related_query_name='user',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='permissões do usuário',
        blank=True,
        help_text='Permissões específicas para este usuário.',
        related_name='customuser_set',
        related_query_name='customuser',
    )

class CustomGroup(models.Model):
    name = models.CharField('nome', max_length=150, unique=True)
    permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='permissões',
        blank=True,
    )
    description = models.TextField('descrição', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        ordering = ['name']
    
    def __str__(self):
        return self.name