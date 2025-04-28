from django.urls import path
from .view.conselho_tutelar import conselho_tutelar
from .view.creas import creas


app_name = 'municipio'

urlpatterns = [
    
    path('conselho_tutelar/', conselho_tutelar, name='conselho_tutelar'),
    path('creas/', creas, name='creas'),
]