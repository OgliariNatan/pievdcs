"""
URL configuration for MAIN project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:

"""
# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from MAIN.views import( 
    home, relatorios, frase_motivacional,
    encaminhamentos, notificacoes, pre_visualizacao_conteudo, 
    index_tailwind, CustomLoginView, api_tendencia_temporal,
    chat_ia_publico, inserir_noticia_form, inserir_noticia_submit,
    popup_conteudo, gerenciar_noticias, editar_noticia, excluir_noticia
)

app_name = 'MAIN'

urlpatterns = [
    path("home/", home, name="home"),  # Rota para a página inicial após login
    path("frase-motivacional/", frase_motivacional, name="frase_motivacional"),
    path("", index_tailwind, name="index"), #Página inicial one_page sem login com tailwind    
       
    #Login & reset senha & logout
    #path('login/', auth_views.LoginView.as_view(template_name='login.html', next_page='/home/'), name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
   
    path('', include('django.contrib.auth.urls')),  # Inclui as URLs de autenticação padrão do Django

    #pré visualizações
    path("pre_visualizacao_conteudo/<int:pk>/", pre_visualizacao_conteudo, name="pre_visualizacao_conteudo"),
    
    path("relatorios/", relatorios, name="relatorios"),
    path("relatorios/api/tendencia/", api_tendencia_temporal, name="api_tendencia_temporal"),
    path("encaminhamentos/", encaminhamentos, name="encaminhamentos"),
    path("notificacoes/<int:notificacoes>", notificacoes, name="notificacoes"),
    path("chat-ia-publico/", chat_ia_publico, name="chat_ia_publico"),
    path("noticia/inserir/", inserir_noticia_form, name="inserir_noticia_form"),
    path("noticia/inserir/submit/", inserir_noticia_submit, name="inserir_noticia_submit"),
    path("conteudo/<int:pk>/popup/", popup_conteudo, name="popup_conteudo"),
    path("noticia/gerenciar/", gerenciar_noticias, name="gerenciar_noticias"),
    path("noticia/<int:pk>/editar/", editar_noticia, name="editar_noticia"),
    path("noticia/<int:pk>/excluir/", excluir_noticia, name="excluir_noticia"),

    
    path("admin/", admin.site.urls, name="admin"),  # Rota para o admin do Django
    path('seguranca/', include('seguranca_publica.urls')), #destinados a segurança publica
    path('justica/', include('sistema_justica.urls')),  #Destinado aos sistemas de justiças
    path('municipio/', include('municipio.urls')), #Destinado ao municipio
    path('chaining/', include('smart_selects.urls')),# Para selecionar os municipios
    path('mensageria/', include('mensageria.urls')), #Para o sistema de mensagens



] + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
    ) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
