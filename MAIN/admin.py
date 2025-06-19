# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ConteudoHome

@admin.register(ConteudoHome)
class ConteudoHomeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'secao', 'autor', 'data_publicacao', 'publicado', 'preview_link')
    list_filter = ('data_publicacao', 'secao', 'autor')
    search_fields = ('titulo', 'texto')

    def preview_link(self, obj):
        url = reverse('pre_visualizacao_conteudo', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Pré-visualizar</a>', url)
    
    preview_link.short_description = 'Visualização'


