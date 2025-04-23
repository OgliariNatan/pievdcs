from django.urls import path
from .views.penal import penal
from .views.militar import militar

app_name = 'seguranca_publica'

urlpatterns = [
    path('penal/', penal, name='penal'),
    path('militar/', militar, name='militar'),
]

# Rotas do app
