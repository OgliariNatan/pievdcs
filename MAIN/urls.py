"""
URL configuration for MAIN project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from MAIN.views import home, index, relatorios, encaminhamentos, notificacoes, pre_visualizacao_conteudo, index_controlador, index_tailwind, CustomLoginView

app_name = 'MAIN'

urlpatterns = [
    path("home/", home, name="home"),  # Rota para a página inicial após login
    #path("", index_controlador, name="index"), #Página inicial one_page sem login
    path("", index_tailwind, name="index"), #Página inicial one_page sem login com tailwind    
    #path("", index, name="index"), #Página inicial one_page sem login
    
    #Login & reset senha & logout
    #path('login/', auth_views.LoginView.as_view(template_name='login.html', next_page='/home/'), name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
   
    path('', include('django.contrib.auth.urls')),  # Inclui as URLs de autenticação padrão do Django

    #pré visualizações
    path("pre_visualizacao_conteudo/<int:pk>/", pre_visualizacao_conteudo, name="pre_visualizacao_conteudo"),
    
    path("relatorios/", relatorios, name="relatorios"),
    path("encaminhamentos/", encaminhamentos, name="encaminhamentos"),
    path("notificacoes/<int:notificacoes>", notificacoes, name="notificacoes"),
    #path("notificacoes/", notificacoes, name="notificacoes"),
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
