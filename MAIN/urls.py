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
from MAIN.views import home, index, relatorios, encaminhamentos, notificacoes, pre_visualizacao_conteudo, index_controlador

app_name = 'MAIN'

urlpatterns = [
    path("home/", home, name="home"),  # Rota para a página inicial após login
    path("", index_controlador, name="index"), #Página inicial one_page sem login
    
    #path("", index, name="index"), #Página inicial one_page sem login
    #Login & reset senha & logout
    path('login/', auth_views.LoginView.as_view(template_name='login.html', next_page='/home/'), name='login'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

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

] + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
    ) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
