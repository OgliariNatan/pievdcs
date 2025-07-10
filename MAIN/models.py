# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import User



secao_choices = (
    ('seguranca_publica', 'Segurança Pública'),
    ('sistema_justica', 'Sistema de Justiça'),
    ('municipio', 'Município'),
    ('leis', 'Leis'),
    ('noticias', 'Notícias'),
    ('sobre', 'Sobre'),
)


class ConteudoHome(models.Model):
    titulo =models.CharField(
        max_length=200,
        verbose_name="Título",
    )
    texto = models.TextField(
        verbose_name="Texto",
    )
    imagem = models.ImageField(
        upload_to='img_home/',
        null=True, blank=True,
        verbose_name="Imagem",
    )
    video = models.FileField(
        upload_to='videos/',
        null=True, blank=True,
        verbose_name='Vídeo',
    )

    publicado = models.BooleanField(
        default=True,
        verbose_name="Publicar na página Inicial?",
    )
    autor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Autor",
        related_name='conteudos_home',  # Adiciona um nome de relacionamento para o autor
    )
    data_publicacao = models.DateTimeField(
        #auto_now_add=True,
        default= timezone.now,
        verbose_name="Data de Publicação",
    )

    link = models.URLField(
        max_length=150,
        null=True, blank= True,
        verbose_name= "Link",
    )
    
    data_expiracao = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Data de Expiração",
    )
    secao = models.CharField(
        max_length=50,
        choices=secao_choices,
        default='noticias',
        verbose_name="Seção",
    )

    def __str__(self):
        return f'{self.titulo} - {self.data_publicacao.strftime("%d/%m/%Y")}'
    
    class Meta:
        verbose_name = "Conteúdo da Página Inicial"
        verbose_name_plural = "Conteúdos da Página Inicial"
        ordering = ['-data_publicacao']