from django.urls import path
from .view.conselho_tutelar import conselho_tutelar
from .view.creas import creas
from .view.cras import cras
from .view.caps import caps
from .view.secretaria_saude import secretaria_saude


app_name = 'municipio'

urlpatterns = [
    
    path('conselho_tutelar/', conselho_tutelar, name='conselho_tutelar'),
    path('creas/', creas, name='creas'),
    path('cras/', cras, name='cras'),
    path('caps/', caps, name='caps'),
    path('secretaria_saude/', secretaria_saude, name='secretaria_saude'),
]