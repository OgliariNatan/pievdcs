from django.urls import path
from .views.penal import penal
from .views.militar import militar
from .views.civil import civil

app_name = 'seguranca_publica'

urlpatterns = [
    path('penal/', penal, name='penal'),
    path('militar/', militar, name='militar'),
    path('civil/', civil, name='civil'),
]

# Rotas do app
