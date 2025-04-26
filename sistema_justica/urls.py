from django.urls import path
from .views.poder_judiciario import poder_judiciario
from .views.ministerio_publico import ministerio_publico
from .views.defensoria_publica import defensoria_publica

app_name = 'sistema_justica'

urlpatterns = [

    path('poder_judiciario/', poder_judiciario, name='poder_judiciario'), #Relacionado ao judiciario    
    path('ministerio_publico/', ministerio_publico, name='ministerio_publico'), #Relacionado ao ministerio publico
    path('defensoria_publica/', defensoria_publica, name='defensoria_publica'), #Relacionado ao defensoria publica 
]