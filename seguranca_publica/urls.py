from django.urls import path
from .views.penal import penal

app_name = 'seguranca_publica'

urlpatterns = [
    path('penal/', penal, name='penal'),
]

# Rotas do app
