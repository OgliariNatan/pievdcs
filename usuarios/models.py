import os
from django.core.exceptions import ValidationError
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

    # Valida arquivo .pdf
    def validate_pdf_file(value):
        ext = os.path.splitext(value.name)[1]
        if ext.lower() != '.pdf':
            raise ValidationError('Apenas arquivos .pdf são permitidos.')

    cpf = models.CharField(
        'CPF',
        max_length=14,
        unique=True,
        validators=[cpf_validator],
        help_text='Formato: 000.000.000-00',
        null=True,
        blank=True
    )
    data_nascimento = models.DateField(
        verbose_name='Data de Nascimento',
        null=True,
        blank=True
    )
    genero = models.CharField(
        verbose_name='Gênero',
        max_length=10,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Feminino'),
            ('N', 'Prefiro não informar'),
        ],
        null=True,
        blank=True
    )
    telefone = models.CharField(
        verbose_name='Telefone',
        max_length=15,
        validators=[phone_validator],
        help_text='Formato: (00) 00000-0000',
        null=True,
        blank=True
    )
    
    foto = models.ImageField(
        verbose_name='Foto do Perfil',
        upload_to='usuarios/fotos/%Y/%m/',
        null=True,
        blank=True,
    )

    departamento = models.CharField(
        verbose_name='Departamento',
        max_length=100,
        null=True,
        blank=True,
        choices=[
            ('Poder Judiciário', 'Poder Judiciário'),
            ('Ministério Público', 'Ministério Público'),
            ('Defensoria Pública', 'Defensoria Pública'),
            ('Polícia Civil', 'Polícia Civil'),
            ('Polícia Militar', 'Polícia Militar'),
            ('Polícia Penal', 'Polícia Penal'),
            ('Polícia Científica', 'Polícia Científica'),
            ('CAPS', 'CAPS'),
            ('Conselho Tutelar', 'Conselho Tutelar'),
            ('CRAS', 'CRAS'),
            ('CREAS', 'CREAS'),
            ('Secretaria da Saúde', 'Secretaria da Saúde'),
            ('Administração', 'Administração')
        ]
    )

    comprovante_vinculo = models.FileField(
        verbose_name='Comprovante de Vínculo',
        upload_to='usuarios/comprovantes/%Y/%m/',
        validators=[validate_pdf_file],
        null=True,
        blank=True,
    )

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
    description = models.TextField(
        verbose_name='descrição',
        blank=True
    )
    created_at = models.DateTimeField(
        verbose_name='criado em', 
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='atualizado em',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        ordering = ['name']
    
    def __str__(self):
        return self.name